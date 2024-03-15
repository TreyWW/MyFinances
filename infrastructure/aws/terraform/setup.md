

# Setup Terraform

1. Install Terraform
2. Run "terraform init"
3. Create a "terraform.tfvars.json" file
4. Add the default values to tfvars but change to fit your needs

```terraform
region              = "eu-west-2"
vpc_cidr            = "172.31.0.0/16"
public_subnet_cidr  = "172.31.16.0/20"
private_subnet_cidr = "172.31.64.0/22"
public_subnet_az    = "eu-west-2a"
private_subnet_az   = "eu-west-2a"

SITE_URL = "myfinances.mydomain.com"
SITE_NAME = "myfinances"
```

5. Generate a API scheduler API key from django using "py manage.py generate_aws_scheduler_apikey" from the **root** of 
   /Myfinances

6. Add this to tfvars as
```terraform
api_destination-api_key = "<CODE THAT YOU JUST CREATED>"
```

7. Run these imports **ONLY IF** you have them created already

```shell
terraform import aws_vpc.main-vpc <your vpc ID>
```