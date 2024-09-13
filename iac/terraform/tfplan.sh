#!/bin/zsh

arg=$1

if [[ -z $arg ]]; then
    arg='dev'
    echo "No argument provided, defaulting to dev"
fi

if [[ $arg != 'dev' && $arg != 'qa' ]]; then
    echo "Invalid environment"
    exit -1
fi

target_tf_workspace="$arg"
tf_workspace=$(terraform workspace show)

if [[ $tf_workspace != $target_tf_workspace ]]; then
    terraform workspace select $target_tf_workspace
fi

echo "Planning for... $arg in $target_tf_workspace"
terraform plan -out "$arg-plan.tfplan" -var-file="env/$arg.tfvars"
