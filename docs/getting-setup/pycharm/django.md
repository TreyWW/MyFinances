## Setting up Django With PyCharm Professional

To setup django, which is our backend library, the main thing you need to do is install dependencies, setup environment variables,
and run server. For more details, view the page for your environment below

1. Fork our repo, follow [our guide](https://github.com/TreyWW/MyFinances/wiki/Fork-the-main-repo) to do that

2. Go into PyCharm, and press `Files (4 Vertical lines at top right)` -> `Open...`

3. Click on the folder you created of the clone in step 1

<details>
<summary>:framed_picture: View Image</summary>
<img src="_assets/setup/pycharm-1-1.png" />
</details>

4. Press `Ok` and open it in a new tab

5. Go to `settings in top right` or using `(ctrl + alt + s)`

<details>
<summary>:framed_picture: View Image</summary>
<img src="_assets/setup/pycharm-2-1.png" />
</details>

6. Now go to your project on the left, and go to "`Python Interpreter`"

<details>
<summary>:framed_picture: View Image</summary>
<img src="_assets/setup/pycharm-4-1.png" /></details>

7. Now add a `local interpreter` and select it

<details>
<summary>:framed_picture: View Image</summary>
<img src="_assets/setup/pycharm-5-1.png" />
</details>

8. Create a `local interpreter`

<details>
<summary>:framed_picture: View Image</summary>
<img src="_assets/setup/pycharm-6-1.png" />
</details>

<br>

!> Before continuing, please install all of our dependencies via `poetry install`"

9. To refresh the cache, go back to settings, project, and interpreter and install "Django" if not already there

<details>
<summary>:framed_picture: View Image</summary>
<img src="_assets/setup/pycharm-6-2.png" />
</details>

10. Go to "`Languages And Frameworks`" -> "`Django`"
    Tick "`Enable Django Support`"
    Make sure Settings, Project Root and Manage script are all set to the correct values

<details>
<summary>:framed_picture: View Image</summary>
<img src="_assets/setup/pycharm-7-1.png" /></details>

11. Now you need to add django to your runners. Go to "current file" at the top, and press edit configurations

<details>
<summary>:framed_picture: View Images</summary>
<img src="_assets/setup/pycharm-8-1.png" />
<img src="_assets/setup/pycharm-8-2.png" />
</details>

12. Setup your database [(click to view our guide)](getting-setup/databases/)