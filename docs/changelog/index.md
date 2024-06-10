# Changelog

!!! danger "Pre-releases"
	We are currently still in development, and our project should **NOT** be considered usable for production yet.

We may not add a changelog entry for every version, it depends how severe the changes are. You can look at the Git Tags page on github to see all of the changes.

???+ tip "v0.4.0 (latest)"
	=== "Additions"
		- 💼 Invoice column rename by @Domejko in [(313)](https://github.com/TreyWW/MyFinances/pull/313)
		- 📧 Users allowed to send emails by @TreyWW in [(314)](https://github.com/TreyWW/MyFinances/pull/314)
		- 💵 Receipt accepts up to two decimal points by @ryansurf in [(330)](https://github.com/TreyWW/MyFinances/pull/330)
		- ⚙️ Feature/conditional checks by @introkun in [(306)](https://github.com/TreyWW/MyFinances/pull/306)
		- ⏰ Invoice reminders by @TreyWW in [(339)](https://github.com/TreyWW/MyFinances/pull/339)
		- 💰 [revamp] Implement price filter receipt by @TreyWW in [(341)](https://github.com/TreyWW/MyFinances/pull/341)
		- 🔀 Make the switcher in sort invoices by @spalominor in [(307)](https://github.com/TreyWW/MyFinances/pull/307)
		- 🚀 Added HTMX Boosting to improve site performance by @TreyWW in [(345)](https://github.com/TreyWW/MyFinances/pull/345)
		- 🎨 Enhanced invoice banner by @TreyWW in [(354)](https://github.com/TreyWW/MyFinances/pull/354)
	=== "Bug Fixes"
		- Correct deployment menu in Invoices->Add Services in the mobile devices by @spalominor in [(301)](https://github.com/TreyWW/MyFinances/pull/301)
		- fixed when creating receipt and deleting the receipts  by @atulanand25 in [(326)](https://github.com/TreyWW/MyFinances/pull/326)
		- Login page broken on mobile - #333 by @CKsabari2001 in [(338)](https://github.com/TreyWW/MyFinances/pull/338)
		- Mypy import errors fix by @Domejko in [(318)](https://github.com/TreyWW/MyFinances/pull/318)
		- 311: Favicon infinite redirect by @introkun in [(312)](https://github.com/TreyWW/MyFinances/pull/312)
		- bug 342 by @atulanand25 in [(343)](https://github.com/TreyWW/MyFinances/pull/343)
		- Mypy type errors fix by @Domejko in [(324)](https://github.com/TreyWW/MyFinances/pull/324)
		- Mypy fixes by @blocage in [(344)](https://github.com/TreyWW/MyFinances/pull/344)
		- 321: Failed to launch app by @introkun in [(322)](https://github.com/TreyWW/MyFinances/pull/322)
		- Anonymous invoice view by link is broken by the currency symbol … by @introkun in [(300)](https://github.com/TreyWW/MyFinances/pull/300)
		- Mypy type errors fix by @Domejko in [(348)](https://github.com/TreyWW/MyFinances/pull/348)
		- Price in the invoice is missing currency symbol by @introkun in [(310)](https://github.com/TreyWW/MyFinances/pull/310)
		- fixed top banner for invoice preview for users that are not logged in by @glizondo in [(349)](https://github.com/TreyWW/MyFinances/pull/349)
	=== "Links"
		- [difference](https://github.com/TreyWW/MyFinances/compare/v0.3.0...v0.4.0)
		- [tag](https://github.com/TreyWW/MyFinances/releases/tag/v0.4.0)

??? abstract "v0.3.0"
	=== "Additions"
		- 🏷 Added invoice **discounts** ([#244](https://github.com/TreyWW/MyFinances/pull/244))
		- 🖼 Added invoice overview page ([#222](https://github.com/TreyWW/MyFinances/pull/222))
		- 📨 Added **email** support ([#208](https://github.com/TreyWW/MyFinances/pull/208))
		- 🧾 Improved invoice design ([#202](https://github.com/TreyWW/MyFinances/pull/202))
		- ⏰ Added invoice schedules ([#220](https://github.com/TreyWW/MyFinances/pull/220))
		- 📁 Usage quotas ([#263](https://github.com/TreyWW/MyFinances/pull/263))
		- 🎣 Pre-Commit hooks ([#257](https://github.com/TreyWW/MyFinances/pull/257))
		- 📚 Improved documentation
	=== "Bug Fixes"
		- Tear down receipt bug on windows fixed ([#218](https://github.com/TreyWW/MyFinances/pull/218))
		- Users currency wasn't shown in invoice ([#260](https://github.com/TreyWW/MyFinances/pull/260))
		- User not able to view invoice if it had a total price of 0 ([#266](https://github.com/TreyWW/MyFinances/pull/266))
		- Improved the email verification message ([#269](https://github.com/TreyWW/MyFinances/pull/269))
		- Fixed bug that didn't let invoices be edited ([#268](https://github.com/TreyWW/MyFinances/pull/268))
		- Fixed scaling issues on the invoice when printing ([#262](https://github.com/TreyWW/MyFinances/pull/262))
		- Fixed invoice bar overlap on mobile ([#284](https://github.com/TreyWW/MyFinances/pull/284))
		- Invoice "TO" client details didn't get pre-filled ([#273](https://github.com/TreyWW/MyFinances/pull/273))
		- Fixed settings page overflow on mobile ([#291](https://github.com/TreyWW/MyFinances/pull/291))
	=== "Links"
		- [difference](https://github.com/TreyWW/MyFinances/compare/v0.2.1...v0.3.0)
		- [tag](https://github.com/TreyWW/MyFinances/releases/tag/v0.3.0)

??? abstract "v0.2.1"
	=== "Additions"
		- 🚩 Added **feature flags**
		- 🐘 Added more **postgres** support
		- 🚅 Added **cache** settings
		- 🎉 **Deployment** has been **successful** and will now undergo more testing!
		- 👋 Possible clients already interested and ready for official launches!
	=== "Links"
		- [difference](https://github.com/TreyWW/MyFinances/compare/v0.2.0...v0.2.1)
		- [tag](https://github.com/TreyWW/MyFinances/releases/tag/v0.2.1)


??? abstract "v0.2.0"
	=== "Additions"
		* 👥 Added **Teams** functionality
		* 🐘 Added **PostgreSQL** database support
		* 🐧 Added **matrix** support so we can now run tests with multiple django versions and multiple ubuntu versions
		* 🧾 Added PDF Upload option for receipts
		* 🧹 Added djLint for HTML file linting
		* 📦 Ready to start getting the product ready for pre-production and more testing
	=== "Links"
		- [difference](https://github.com/TreyWW/MyFinances/compare/v0.1.2...v0.2.0)
		- [tag](https://github.com/TreyWW/MyFinances/releases/tag/v0.2.0)

??? abstract "v0.1.2"
	=== "Additions"
		* 📦 Added [python poetry](https://python-poetry.org/)
		* ✏️ Added the ability to edit invoices
		* 📜 Added [hyperscript](https://hyperscript.org/)
		* 🧾 Added more info for receipts & the ability to SAFELY download them
		* 🐬 Fixed docker builds, now uses poetry, and runs much faster
	=== "Links"
		- [difference](https://github.com/TreyWW/MyFinances/compare/v0.1.1...v0.1.2)
		- [tag](https://github.com/TreyWW/MyFinances/releases/tag/v0.1.2)
??? abstract "v0.1.1"
	=== "Additions"
		* Added documentation
		* Added social logins (github + google)
		* Added custom colours for tailwind theme
		* Added signal for UserSettings addition on user creation
	=== "Links"
		- [difference](https://github.com/TreyWW/MyFinances/compare/v0.1.0...v0.1.1)
		- [tag](https://github.com/TreyWW/MyFinances/releases/tag/v0.1.1)
??? abstract "v0.1.0"
	=== "Overview"
		First release of the project!
	=== "Additions"
    	* 🧾 Receipts
		* 📜 Invoices
		* 🧔 Account Management
	=== "Links"
		- [tag](https://github.com/TreyWW/MyFinances/releases/tag/v0.1.0)
