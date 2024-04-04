---
status: deprecated
---

!!! danger
    This feature has been deprecated in favour of local feature flags.

# Feature flags with AWS

Be sure to check out the [pricing page](https://aws.amazon.com/config/pricing/) of AWS before setting this up so you don't get an
unexpected bill :)

## Setup on AWS

1. Go to AWS Systems Manager
2. Go to "**AppConfig**"
3. Create an "**Application**"
    - Note down the name for later [APPLICATION_NAME]
    - No extensions are needed
    - Press Create Application
4. Go to your new application
5. Press "**Create Environment**" on the "**Environments**" tab
    - Note down the name for later [ENVIRONMENT_NAME]. E.g. I'm calling mine "Staging"
    - You don't need a monitor or extensions
    - Press Create environment
6. "**Create**" a new profile on the "**Configuration Profile and Feature Flag**" tab
    - Choose the "Feature Flag" profile type
    - Note down the name for later [PROFILE_NAME]. E.g. I'm calling mine "myfinances"
    - You don't need extensions
    - Press "Create feature flag configuration profile"
7. Add these environment variables

```dotenv
AWS_FEATURE_FLAGS_ENABLED=True
AWS_FEATURE_FLAGS_APPLICATION=[APPLICATION_NAME]
AWS_FEATURE_FLAGS_ENVIRONMENT=[ENVIRONMENT_NAME]
AWS_FEATURE_FLAGS_PROFILE=[PROFILE_NAME]
AWS_FEATURE_FLAGS_UPDATE_CHECK_INTERVAL=45 # This can be any interval (in seconds)
```

## Create a new feature flag

Make sure you have set AppConfig up first, then you can start creating flags.

1. Go to your Application.
2. Go to your Configuration Profile, E.g. mine is called myfinances (your [PROFILE_NAME])
3. Press "**Add new flag**"
    - Add a name and key (they can be the same)
    - Press Add flag
4. Toggle the flag on/off at the bottom
5. Press "Save new version"

### Deploy the flags to your environment

1. Once the version is saved, you can press "**Start deployment**"
    - Environment will be your [ENVIRONMENT_NAME]. E.g. Mine is "Staging"
    - Set your Deployment strategy, I use `AppConfig.AllAtOnce (QUICK)`, though AWS do recommend `Linear20PercentEvery6Minutes`.
      Up to you based on your deployment whether you're production or staging.
    - Done! MyFinances will pick this up within [UPDATE_CHECK_INTERVAL] time, without any restart!

## Official Feature Flag List

Please keep in mind if you have AWS_FEATURE_FLAGS_ENABLED set to True, any flags that aren't created will be set to False.
This may break core functionality such as allowing signups. Makes sure you add all of these feature flags to your AWS Flags.

|     Flag Name     | Data Type | Example |                   Description                   |
|:-----------------:|:---------:|:-------:|:-----------------------------------------------:|
| areSignupsEnabled |  Boolean  |  True   | Whether new user registration should be allowed |
