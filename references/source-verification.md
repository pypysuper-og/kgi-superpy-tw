# Sources and verification scope

The references in this skill are development notes. Select the relevant market and operation, then confirm the exact contract needed for the task. Do not assume every field in these notes has been checked against the current website or installed SDK.

## Choose an appropriate source

- Use the [official link index](official-index.md) to find public function pages. The [US API index](https://superpy.kgieworld.com.tw/kgipythonapi/guide/us/member) and [domestic futures index](https://superpy.kgieworld.com.tw/kgipythonapi/guide/fut/member) cover different markets; do not construct other market URLs by analogy.
- Check the [official release page](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/version) and installed package version when compatibility matters. A package release, a website description and an observed runtime result are separate evidence.
- Treat SDK implementation observations as version-specific. Use supported interfaces in generated application code; private caches or internal components do not become supported integration points because their implementation was inspected.
- Application state models, UI/UX patterns and engineering-partner prompts are design references. The executable practical cases use synthetic events and do not establish broker behavior.

Only publish source identifiers, quotations and examples that are suitable for public sharing. Do not attach private source metadata to public skill content.

## Resolve an affected contract

Check exact facade and enum spelling, method parameters, return fields, units and lifecycle order. Returned fields do not establish accepted input parameters, and similar method names across markets do not establish equivalent semantics.

When sources disagree or a relevant page cannot be accessed, preserve the uncertainty and identify the affected call. Check the target SDK or obtain confirmation before implementing that call. Do not guess keyword arguments, try alternate identifiers through live mutations, or describe an unchecked note as an official public contract. Continue work that does not depend on the unresolved point.

## Interpret the evidence

- Syntax checks establish parseability; synthetic models establish only the modeled behavior.
- A dated SDK or runtime observation applies to that version, environment and operation. It is not a general service guarantee.
- Historical evaluation hashes identify the original candidates. Updating documentation does not update those candidates or extend their scores to the current skill.
- Live login, market-data delivery, order handling and recovery need their own evidence and the existing authorization for those effects.
