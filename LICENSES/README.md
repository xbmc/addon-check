![Kodi Logo](https://github.com/xbmc/xbmc/blob/master/docs/resources/banner_slim.png)

# Kodi addon-check's licensing rules
Kodi addon-check is provided under the terms of the GNU General Public License v3.0.

The license described in the **[LICENSE](https://github.com/xbmc/addon-check/blob/master/LICENSE)** file applies to **Kodi addon-check's source as a whole**, though individual source files can have a different license which is required to be compatible with the **GPL-3.0**. Aside from that, individual files can be provided under a dual license, e.g. one of the compatible GPL variants and alternatively under a permissive license like BSD, MIT etc.

## The SPDX License Identifier
The common way of expressing the license of a source file is to add the matching boilerplate text into the top comment of the file. Due to formatting, typos etc. these "boilerplates" are hard to validate for tools which are used in the context of license compliance.

An alternative to boilerplate text is the use of Software Package Data Exchange (SPDX) license identifiers in each source file. SPDX license identifiers are machine parsable and precise shorthands for the license under which the content of the file is contributed. SPDX license identifiers are managed by the SPDX Workgroup at the Linux Foundation and have been agreed on by partners throughout the industry, tool vendors, and legal teams. For further information see **[spdx.org](https://spdx.org/)**.

Kodi addon-check requires the precise SPDX identifier in all source files. The valid identifiers used in Kodi addon-check have been retrieved from the official **[SPDX License List](https://spdx.org/licenses/)** along with the license texts.

### License Identifier Placement
The SPDX license identifier in Kodi addon-check files shall be added at the top of the file.

### License Identifier Syntax
A `<SPDX License Expression>` is either an SPDX short form license identifier found on the **[SPDX License List](https://spdx.org/licenses/)**, or the combination of two SPDX short form license identifiers separated by `WITH` when a license exception applies. When multiple licenses apply, an expression consists of keywords `AND`, `OR` separating sub-expressions. See SPDX License Expression **[usage guide](https://spdx.org/ids)** for more information.

### License Identifier Style
The SPDX license identifier is added in the form of a comment. The comment style depends on the file type. For a Python source file, the format must be

```
/*
 *  Copyright (C) <year> <copyright holders>
 *  This file is part of <software> - <URL>
 *
 *  SPDX-License-Identifier: <SPDX License Expression>
 *  See <license file/license index file> for more information.
 */
```

Since most source files in Kodi addon-check are `GPL-3.0-only` licensed, the typical copyright notice will look like this:
```
/*
 *  Copyright (C) 2017-2018 Team Kodi
 *  This file is part of Kodi - https://kodi.tv
 *
 *  SPDX-License-Identifier: GPL-3.0-only
 *  See LICENSES/README.md for more information.
 */
```

**NOTE:** Kodi addon-check is developed and maintained by Kodi Team members and the open-source community. We thank all of our **[contributors](https://github.com/xbmc/addon-check/graphs/contributors)**! **For the detailed history of contributions** of a given file, use `git blame <filename>` to see line-by-line credits or `git log --follow <filename>` to see the changelog across renames, rewrites and code shuffle.

### License Files
All SPDX license identifiers must have a corresponding file in the **LICENSES** subdirectory. This is required to allow tool verification (e.g. **[ScanCode toolkit](https://github.com/nexB/scancode-toolkit)**) and to have the licenses ready to read and extract right from the source, which is recommended by various FOSS organizations, e.g. the **[FSFE REUSE Initiative](https://reuse.software/)**.

The typical license file looks like this:
```
Valid-License-Identifier: GPL-3.0-only
SPDX-URL: https://spdx.org/licenses/GPL-3.0-only.html
Usage-Guide:
  To use the GNU General Public License v3.0 or later put the following SPDX
  tag/value pair into a comment according to the placement guidelines in
  the licensing rules documentation:
    SPDX-License-Identifier: GPL-3.0-only
License-Text:
  Full license text
```

Kodi addon-check currently contains files and code licensed under:

* **[GPL-3.0-only](GPL-3.0-only)**: GNU General Public License v3.0 only

These licensing rules were adapted from the **[Linux kernel licensing rules](https://github.com/torvalds/linux/blob/master/Documentation/process/license-rules.rst)**.
