# QuakeNite

**QuakeNite** is a fast-paced arena shooter that combines classic **Quake-style movement and gameplay** with **Fortnite-style building mechanics**. Build walls, ramps, and platforms on the fly while bunny-hopping, rocket-jumping, and fragging your opponents in intense multiplayer battles.

## About

QuakeNite is forked from [iortcw](https://github.com/iortcw/iortcw), a community-maintained port of Return to Castle Wolfenstein (RTCW). We've taken the solid foundation of the id Tech 3 engine and enhanced it with real-time building mechanics inspired by Fortnite, creating a unique blend of old-school arena shooter skill and modern tactical construction.

### Key Features

  * **Fortnite-Style Building** - Construct walls, floors, ramps, and roofs in real-time during combat
  * **Quake-Style Movement** - Classic bunny-hopping, strafe-jumping, and rocket-jumping mechanics
  * **Fast-Paced Arena Combat** - Intense multiplayer battles with classic weapon pickups and power-ups
  * **Build Battles** - Outbuild and outshoot your opponents in vertical combat encounters
  * **SDL Backend** - Modern cross-platform support
  * **OpenAL Sound** - High-quality 3D audio with multiple speaker support
  * **Full x86_64 Support** - Native 64-bit performance
  * **VoIP Support** - Built-in voice chat and Mumble integration
  * **Cross-Platform** - Windows, Linux, and macOS support
  * **HTTP/FTP Downloads** - Fast content downloading using cURL
  * **PNG Support** - Modern texture format support

### Gameplay

QuakeNite takes the precision aiming and movement mastery of classic arena shooters and adds a new dimension with real-time building. Players can:

- Build defensive structures to block incoming fire
- Create ramps and platforms to gain height advantage
- Edit and destroy builds to outplay opponents
- Combine building with rocket-jumping for advanced movement

The result is a game where mechanical skill in both shooting AND building determines the victor.

## Quick Start Guide

  1. Download the latest QuakeNite release for your operating system.
  2. Extract the release zip into your desired installation directory (e.g., `C:\Games\QuakeNite\` on Windows or `/home/user/Games/QuakeNite/` on Linux).
  3. Run the QuakeNite executable to start playing!

## Compilation and Installation

### For Linux/*nix

  1. Change to the directory containing this readme.
  2. Run `make`.

### For Windows

Please refer to the HOWTO-Build.txt file contained within this repository.

### For macOS (Universal Binary)

  1. Install MacOSX SDK packages from Xcode.
  2. Change to the directory containing the game source you wish to build.
  3. Run `./make-macosx-ub.sh`
  4. Copy the resulting app in `/build/release-darwin-ub` to your Applications folder.

### Installation (Linux/*nix)

  1. Set the COPYDIR variable in the shell to be where you want QuakeNite installed. By default it will be `/usr/local/games/quakenite`.
  2. Run `make copyfiles`.

## Build Configuration

The following variables may be set, either on the command line or in Makefile.local:

  * `CFLAGS` - use this for custom CFLAGS
  * `V` - set to show cc command line when building
  * `BUILD_SERVER` - build the dedicated server binary
  * `BUILD_CLIENT` - build the client binary
  * `BUILD_BASEGAME` - build the base game binaries
  * `BUILD_GAME_SO` - build the game shared libraries
  * `BUILD_GAME_QVM` - build the game QVMs
  * `BUILD_STANDALONE` - build binaries suited for stand-alone games
  * `USE_OPENAL` - use OpenAL where available
  * `USE_CURL` - use libcurl for HTTP/FTP download support
  * `USE_VOIP` - enable built-in VoIP support
  * `USE_MUMBLE` - enable Mumble support

## Building Controls

QuakeNite adds the following building controls:

| Action | Default Bind |
|--------|--------------|
| Build Wall | Q |
| Build Floor | F |
| Build Ramp | C |
| Build Roof | V |
| Edit Build | G |
| Rotate Build | R |

## Contributing

QuakeNite is open source and we welcome contributions! Please send all patches as a pull request on GitHub.

When contributing, please keep in mind:
- QuakeNite focuses on combining arena shooter mechanics with building gameplay
- Performance optimizations are always welcome
- New building features and improvements are encouraged
- Bug fixes and cross-platform improvements are appreciated

## Credits

### QuakeNite Team
QuakeNite is developed by the QuakeNite community.

### Based on iortcw
QuakeNite is built on the excellent work of the iortcw maintainers:
  * Donny Springer
  * Zack Middleton
  * James Canete

### Original RTCW
Return to Castle Wolfenstein was developed by id Software and Gray Matter Interactive.

### Significant iortcw Contributors
  * Ryan C. Gordon
  * Andreas Kohn
  * Joerg Dietrich
  * Stuart Dalton
  * Vincent S. Cojot
  * optical
  * Aaron Gyes
  * Ludwig Nussel
  * Thilo Schulz
  * Tim Angus
  * Tony J. White
  * Zachary J. Slater

## License

QuakeNite is released under the GNU General Public License v3. See the LICENCE.md file for details.

This project is based on GPL-licensed code from iortcw and the original RTCW source release.
