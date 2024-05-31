# Management Bot

1. In terminal, type
	```
	cd .github/management_bot/pulumi/
	```
2. Go to [Github Apps Settings](https://github.com/settings/apps) and press `New GitHub App`
- Any app name
- Any homepage url
- No callback URL
- Set the webhook URL temporarily to anything like https://example.com
- `Create Github App`
3. Now press "edit" on the github app
4. **copy** the `App ID` field (may look like 912345)
5. Now go back to terminal, and type:
	```
   	pulumi config set --secret app_id <your copied App ID>
	 ```
6. Scroll down to `Private keys` and press `Generate a private key`
7. Copy the generated path of the file it generated
8. Open a new terminal and type
	```
 	python ../../../manage.py encrypt_value file <path>

 	# e.g.
 	python ../../../manage.py encrypt_value file "E:\Downloads\myfinances-management.2024-05-31.private-key.pem"
	```
	- Copy the value that is inputted (not the quotation marks or the first b letter though!)
9. Now go back to terminal, and type:
   ```
   	pulumi config set --secret private_key <private_key_value>
   ```

	!!! danger "Note"
   		If you have spaces in your value, you may need to manually put the value in the `Pulumi.xyz.yaml` file with `>` before
   		the first line.


10. Go to [Github Actions](https://github.com/TreyWW/MyFinances/actions)
- "Click on `"Lambda Zip for Management Bot"`
- Click on the latest run
- Scroll down on the "Summary" tab down to "Artifacts"
- Press on `"python-package"`
11. Unzip the zip to reveal python.zip
12. Copy the path to python.zip
13. Go back to the terminal and type

	```
 	pulumi config set lambda_zip_path <path>
	```

14. Finally you can run

	```
	pulumi up
	```

15. Copy the `"Invoke URL"` from the output, head back over to https://github.com/settings/apps and go to your app settings
 - scroll down to `"Webhook"` and paste the Invoke URL into the Webhook URL field and press `Save changes`

16. Now scroll back up and click on the `"Permissions & Events"`
17. In `"Repository Permissions"` select:
	- Issues (read + write)
    - Metadata (read only)
    - Pull requests (read + write)
18. Scroll down to Subscribe to events and tick
    - Issue Comment
19. Scroll down and press Save Changes
20. Scroll up to `Install App`, and install it to your repositories! Now you can use `/help` in issue comments
