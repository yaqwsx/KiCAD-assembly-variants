# KiCAD-assembly-variants

Assembly variants switcher for KiCAD 6 and 7.

## Installation

Install in KiCAD command prompt via pip:

```
$ pip install -U git+https://github.com/yaqwsx/KiCAD-assembly-variants@main
```

All commands should be invoked from KiCAD command prompt.

## Variant format

The alternative properties are expected to follow `<variant_prefix> <property
name>`. That is, if you want to have alternative values for `Value`, you can
have extra property fields, e.g., `variant1 Value` and `variant2 Value`.

On variant switching, the corresponding alternative field value is copied to the
original one.

The following special attributes names map to KiCAD built-ins:

- Reference
- Value
- in_bom (yes/no)
- on_board (yes/no)
- dnp (yes/no)

## Usage

If you want to switch variant in place, just invoke:
```
$ kiAsm switch --field Value --field Comment --prefix variant1 path/to/project/directory
```

You can specify multiple fields to change and only single prefix. Instead of
`--field` you can use `-f` and instead of `--prefix` you can use `-p`

If you want to export multiple variants, you can use the `export` command:

```
$ $ kiAsm export --field Value --field Comment --prefix variant1 --prefix variant2 path/to/project/directory path/to/output/directory
```

This command will create directories `variant1` and `variant2` in the output
directory and a copy of the project with switched corresponding variant will be
copied there. The original project is not modified.
