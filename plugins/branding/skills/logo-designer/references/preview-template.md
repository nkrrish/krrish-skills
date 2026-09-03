# Preview Template

Write this to `logos/preview.html`. Replace `{{PHASE}}` with `Concepts` or `Iterations`,
`{{CARDS}}` with one card per SVG, and `{{FAVICON_ROW}}` with the size-check strip.

Always regenerate the whole file — do not patch it incrementally.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Logo Preview — {{PHASE}}</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    padding: 2rem;
    transition: background-color .3s, color .3s;
  }
  body.light { background: #f5f5f5; color: #333; }
  body.dark  { background: #1a1a1a; color: #eee; }
  .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
  h1 { font-size: 1.5rem; font-weight: 600; }
  h2 { font-size: 1.1rem; font-weight: 600; margin: 3rem 0 1rem; }
  .toggle {
    padding: .5rem 1rem; border: 1px solid currentColor; border-radius: 6px;
    background: transparent; color: inherit; cursor: pointer; font-size: .875rem;
  }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem; }
  .card { border: 1px solid rgba(128,128,128,.3); border-radius: 12px; overflow: hidden; }
  .card-img { display: flex; align-items: center; justify-content: center; padding: 2rem; min-height: 240px; }
  body.light .card-img { background: #fff; }
  body.dark  .card-img { background: #2a2a2a; }
  .card-img img { max-width: 100%; max-height: 200px; }
  .card-label { padding: .75rem 1rem; font-size: .875rem; font-weight: 500; border-top: 1px solid rgba(128,128,128,.3); }
  body.light .card-label { background: #fafafa; }
  body.dark  .card-label { background: #222; }
  .sizes { display: flex; gap: 2rem; flex-wrap: wrap; align-items: flex-end; }
  .size-group { display: flex; flex-direction: column; align-items: center; gap: .5rem; }
  .size-row { display: flex; gap: 1rem; align-items: flex-end; }
  .size-cell { text-align: center; }
  .size-cell div { font-size: .75rem; opacity: .6; margin-top: .25rem; }
  .name { font-size: .8rem; font-weight: 500; }
</style>
</head>
<body class="light">
  <div class="header">
    <h1>Logo Preview — {{PHASE}}</h1>
    <button class="toggle" onclick="document.body.classList.toggle('dark');document.body.classList.toggle('light');this.textContent=document.body.classList.contains('dark')?'☀️ Light':'🌙 Dark';">🌙 Dark</button>
  </div>

  <div class="grid">
    {{CARDS}}
  </div>

  <h2>Favicon size check</h2>
  <div class="sizes">
    {{FAVICON_ROW}}
  </div>
</body>
</html>
```

## Card

`{{PATH}}` is relative to `logos/` (e.g. `concepts/concept-1.svg`). `{{LABEL}}` is the filename
without extension.

```html
<div class="card">
  <div class="card-img"><img src="{{PATH}}" alt="{{LABEL}}"></div>
  <div class="card-label">{{LABEL}}</div>
</div>
```

## Favicon size cell

One group per mark. Include this from the **first** concept round, not only during refinement —
an icon mark that fails at 32px is out regardless of how it looks large.

```html
<div class="size-group">
  <div class="name">{{LABEL}}</div>
  <div class="size-row">
    <div class="size-cell"><img src="{{FAVICON_PATH}}" width="64" height="64"><div>64</div></div>
    <div class="size-cell"><img src="{{FAVICON_PATH}}" width="32" height="32"><div>32</div></div>
    <div class="size-cell"><img src="{{FAVICON_PATH}}" width="16" height="16"><div>16</div></div>
  </div>
</div>
```

`{{FAVICON_PATH}}` is the mark's own path for an icon mark. For a combination mark, first write a
standalone square SVG containing only the `#icon` group and point at that — never squeeze a
horizontal lockup into a square cell.

## Ordering

- **Concepts**: numeric order, concept-1 first.
- **Iterations**: most recent first, so the newest work is at the top of the page.
