## Setting up our frontend

To setup Tailwind, which is our CSS library, you need to install NPM.

1. Install NPM, you can search this up or follow a guide
   like [this](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).
2. Go to your [forked directory](getting-setup/pycharm/django/fork)
3. Go to a terminal with the forked directory open (can use `cd <directory>`)
4. Run

```bash
npm install
```

*** 

## Build Tailwind

?> You should build tailwind `every time` you want to make any change to the frontend.
<br>Luckily, this is easy with the "watch" command, it auto-builds on any change you make.

```bash
npm run tailwind-build
```

!> Please **never** edit the `output.css` file, always edit the `input.css` file if you need to make manual CSS changes.

