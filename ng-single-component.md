# Angular Single File Component

- src:
  - https://stackoverflow.com/questions/75257318/how-can-i-generate-a-single-file-component-with-angulars-cli
  - https://muhimasri.com/blogs/how-to-create-a-single-file-component-in-angular/

```json
"schematics": {
  "@schematics/angular:component": {
    "standalone": false,
    "inlineStyle": true,
    "inlineTemplate": true,
    "skipTests": true
  },
}
```