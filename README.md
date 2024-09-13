# JIRA 2 ClickUp Integration

## Setup

## Authentication
Function validates that request came from appropriate source by matching the `x-atlassian-webhook-identifier` header to a webhook id, that is configured via environment variable.

# Function Deployment

## Configuring
Following parameters require configuration:
|Parameter|Description|
|--|--|
|JiraSecret|Authentication key sent by JIRA to a webhook.|

## Publishing function app to Azure 

### AZ CLI
Publish function using the function core tools:
```bash
$ func azure functionapp publish dev-jira2clickup-westeurope
```
Make sure that required application related environment varibles are configured in the cloud.

## From 0
### Creating local environment
Install Azure Functions Core Tools: https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local  

Init function:
```bash
func init MyProjFolder --worker-runtime python --model V2
```
Init Python local env, activate and restore dependencies.
```bash
py -m venv .venv
. .venv/bin/activate
py -m pip install -r requirements.txt
```
Run
```bash
func start
```

### End-to-End testing
To test from real JIRA service, tunneling from public internet is required. Simplest solution is `ngrok`.
Run tunnel:
```bash
ngrok http 7071
...
Forwarding                    https://0966-2a02-a317-e48d-100-6479-f5ed-1013-ee06.ngrok-free.app -> http://localhost:7071    
...
```
Use the forwarding URL as a JIRA webhook for Ticket Create/Update event: https://teqniksoft.atlassian.net/plugins/servlet/webhooks  

## IaC
Azure is used for hosting the function, so you need Azure CLI installed.

### Provider authentication
Current approach uses Service Principal with Contributor role for a subscription to auth terraform provider.
Create file _terraform-sp.auto.tfvars_ (files _*.auto.tfvars_ are picked up automatically) with following content:
```
client_id       = "<TF SP client ID>"
client_secret   = "<TF SP secret>"
tenant_id       = "<Azure tenant ID>"
subscription_id = "<Azure Subscription ID>"
```

To get these do the following:
1) List Azure subscriptions
```bash
az account list
```
or using filter
```
az account list --query "[?"[?user.name == '***@outlook.com']"]"
```
2) Select default subscription
```bash
az account set --subscription="SUBSCRIPTION_ID"
```
3) Find service principal for Terraform provider (login if required - you'll be prompted):
```bash
az ad sp list --query "[].[appId,appDisplayName]"  --output tsv
```
If you don't have one, use the following command to create it (record the _appId_ and _password_ they are _client_id_ and _client_secret_ correspondingly):
```bash
az ad sp create-for-rbac --role="Contributor" \
--scopes="/subscriptions/<SUBSCRIPTION_ID>" \
--name TerraformServicePrincipal
```
### Initialize Terraform backend
Create manually (if not exists) storage account and container with defaults, create SAS token (make sure you selected read/write permissions).  
You need them to fill the _backend-config.txt_ file like following example:
```
resource_group_name = "terraform-backend-pl"
container_name = "terraform-states"
storage_account_name = "terraformstatespl"
sas_token = "<SAS token>"
```
Once complete, run to initialize Terraform:
```bash
terraform init -backend-config="env/backend-config.txt"
```

### Switch workspace
We use workspaces to separate environments. Currently effective only the _dev_ workspace.
```bash
terraform workspace new dev
```
OR if you already have it created:
```bash
terraform workspace select dev
```

### Configure deployment
Create (obtain) _env/dev.tfvars_ file with environment-specific configuration variables. They must correspond to variables from _variables.tf_ file.
See configuration section.

## References
JIRA API: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/#version  
JIRA Webhooks: https://teqniksoft.atlassian.net/plugins/servlet/webhooks#  
ClickUp API: https://clickup.com/api/clickupreference/operation/GetTask/  
