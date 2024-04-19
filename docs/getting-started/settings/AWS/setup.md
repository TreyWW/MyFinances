# Setting up AWS

!!! danger
	We are currently not publishing a stable updated copy of the infrastructure deployment. We may update this time to time
	but it will likely not be production ready.

First you'll need to setup an AWS Account and login to the AWS CLI on your device.

You will also need [`pulumi`](https://www.pulumi.com/docs/install/) to be installed. In their installation guide you can also
find the [`Getting started with AWS`](https://www.pulumi.com/docs/clouds/aws/get-started/begin/) guide and try an example
project get a feel.


!!! tip
	Before running `pulumi up` you may want to run `pulumi preview --diff` to see what will actually be modified. Make sure
	nothing important is deleted/changed!


After pulumi is installed you can follow to process below:

```shell
cd infrastructure/aws/pulumi/

pulumi up
```

!!! warning
	You may incur a bill which is not our responsibility. You can use the aws [calculator](https://calculator.aws/#/) to
	calculate what your usage may be.

Now you should see a list of things, use the arrow keys to go down to "details" to see exactly what will be created.

!!! danger
	You may not want to create a new VPC or override an existing one, be careful at this step!


Now as you likely won't want a new or changed VPC (as this can be very dangerous for any existing AWS services using this VPC)
you can import your existing VPC. Go to the ['VPC Console'](https://eu-west-2.console.aws.amazon.com/vpcconsole/home) on AWS
and you will see your VPC, copy the "VPC ID".

Now type in:

```shell
pulumi import aws:ec2/vpc:vpc/Vpc main_vpc [ID OF YOUR VPC]

# e.g. pulumi import aws:ec2/vpc:Vpc main_vpc vpc-01and2357151sounds5501Good73
```

And press "yes". You may want to do the same with the subnets:

```shell
pulumi import aws:ec2/subnet:Subnet main_subnet [YOUR SUBNET ID]

pulumi import aws:ec2/subnet:Subnet private_subnet [YOUR SUBNET ID]
```
