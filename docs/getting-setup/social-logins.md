# Social Login

MyFinances supports social login with manual details and GitHub OAuth.

!> These docs show you how to get setup locally with these
logins, but on production make sure to replace `http://127.0.0.1:8000` with `https://` and then your domain name.

## Set up Social Login with GitHub

1. [In GitHub](https://github.com/), register a new OAuth application and note its client secret and client ID. MyFinances will
   need them to authenticate against GitHub.
    1. Go to **Settings > Developer Settings > OAuth Apps > Register a new application/New OAuth App**
       or click this [link](https://github.com/settings/applications/new).
    2. Fill in the individual fields:

    - Set **Homepage URL** to http://localhost:8000.
    - Set **Authorization callback URL** to http://127.0.0.1:8000/login/external/complete/github/.
    - Fill in other fields according to your preferences. For more information, refer to
      the [GitHub documentation](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app).

    3. Confirm with **Register application**.
       <img src="_assets/setup/social/GitHub_steps1to3.png" />
       You are redirected to a page with your OAuth application.
    4. Click **Generate a new client secret**.
    5. Note the client ID and client secret as you will need to add them to the MyFinances settings.
       <img src="_assets/setup/social/GitHub_steps4to5.png" />

2. Add the client secret and client ID of the OAuth application to the MyFinances settings.
    1. Set the following environment variables in your configuration:
    ```
    GITHUB_SECRET=<GitHub_client_secret>
    GITHUB_KEY=<GitHub_client_ID>
    ```
    2. Restart the application for changes to take effect.

## Set up Social Login with Google

1. [In the GoogleCloud console](https://console.cloud.google.com/), create a new project for MyFinances. Generate a client secret
   and take note of it as well as of the client ID. MyFinances will need them to authenticate against Google.
    1. Create a new project that will represent MyFinances in the GoogleCloud console.
       Click [here](https://console.cloud.google.com/projectcreate) to go to the **New project** page. For more information on how
       to fill in the individual fields, refer to
       the [Google Cloud documentation](https://developers.google.com/workspace/guides/create-project).
    2. Configure the consent screen that will be shown to users when they try to log in to MyFinances.
       Click [here](https://console.cloud.google.com/apis/credentials/consent) to go to the **OAuth consent screen** page. For
       more information on how to fill in the individual fields, refer to
       the [Google Cloud documentation](https://developers.google.com/workspace/guides/configure-oauth-consent#configure_oauth_consent).
    3. Generate OAuth client ID that will be used to authenticate MyFinances against Google's OAuth servers.
       Click [here](https://console.cloud.google.com/apis/credentials) to go to the **Credentials** page. For more information on
       the procedure, refer to
       the [Google Cloud documentation](https://developers.google.com/workspace/guides/create-credentials#oauth-client-id).  
       <img src="_assets/setup/social/Google_step3a.png" />

        - Set **Application type** to *Web Application*.
        - To **Authorized JavaScript origins**, add the following URIs: http://localhost:8000 and http://127.0.0.1:8000.
        - To **Authorized redirect URI**, add the following URI: http://127.0.0.1:8000/login/external/complete/google-oauth2/.
    4. Note the client secret and client ID.<br>
       <img src="_assets/setup/social/Google_step4.png" />

2. Add the client secret and client ID of the OAuth application to the MyFinances settings.
    1. Set the following environment variables in your configuration:
      ```
      GOOGLE_CLIENT_ID=<Google_client_ID>
      GOOGLE_CLIENT_SECRET=<Google_client_secret>
      ```
    2. Restart the application for changes to take effect.