#!/bin/bash

gcloud auth login
gcloud auth application-default login
gcloud config set project $(grep "project_id" terraform/terraform.tfvars | cut -d " " -f 3 | tr -d '"')
