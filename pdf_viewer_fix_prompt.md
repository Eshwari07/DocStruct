# PDF Viewer Rendering Fix
## Prompt for Implementation

---

## Context & Goal

You are working on **DocStruct**, a local document structure extraction tool. The frontend is React + TypeScript + Vite + Tailwind CSS. The PDF viewer uses `react-pdf` (version `^9.1.0`) with `pdfjs-dist`.

**The problem:** The left panel PDF preview is visually broken in two distinct ways visible in the screenshot:

1. **Page content is clipped on the left** — the PDF page renders wider than the panel and gets cut off instead of fitting within the available width
2. **Text layer is floating and misaligned** — the blue text selection highlights and the selectable text appear disconnected from the actual rendered page content, drifting outside the page boundaries

Both bugs have the same root causes. Fix them.

---

## Existing File to Modify

The only file you need to modify is:

**`frontend/src/components/DocumentViewer/PdfViewer.tsx`**

You will also need to check and potentially update:

**`frontend/src/main.tsx`** or **`frontend/src/styles.css`** — for CSS imports

Read the full current `PdfViewer.tsx` source carefully before changing anything. It uses:
- `react-pdf`: `Document`, `Page`, `pdfjs`
- Zustand store via `useDocStructStore`
- IntersectionObserver for scroll-tracking across all rendered pages
- `useCallback`, `useEffect`, `useMemo`, `useRef`, `useState`
- The `<Page>` component is rendered for every page in a `Array.from({ length: pdfNumPages })` loop

---

## Root Cause Analysis

### Bug 1: Missing TextLayer and AnnotationLayer CSS

`react-pdf` v9 renders the text layer and annotation layer as absolutely-positioned DOM elements overlaid on the canvas. These elements require specific CSS to be clipped and positioned correctly relative to the page canvas. Without this CSS:
- The text spans float at arbitrary positions on screen
- Text selection highlights appear disconnected from the visual page
- Annotations (links, form fields) appear in wrong positions

**The fix:** Import both CSS files that `react-pdf` ships with. These must be imported **once** globally, before any `<Page>` renders. Add these two imports to `frontend/src/styles.css` (so they load with the app):

```css
@import 'react-pdf/dist/Page/TextLayer.css';
@import 'react-pdf/dist/Page/AnnotationLayer.css';
```

Or alternatively, import them in `frontend/src/main.tsx`:
```typescript
import 'react-pdf/dist/Page/TextLayer.css';
import 'react-pdf/dist/Page/AnnotationLayer.css';
```

Pick **one** location — do not import both places. `main.tsx` is preferable because the import order is explicit and CSS-in-JS won't interfere.

### Bug 2: Page width overflows the panel container

The `<Page>` component from `react-pdf` renders at the PDF's intrinsic size multiplied by the `scale` prop. For a standard US Letter PDF at `scale={1.2}`, this is approximately 792px wide. The left panel in DocStruct is roughly 50% of the viewport width — often less than 792px on typical screens.

The scroll container has `overflow-x-auto` which allows horizontal scrolling, but the panel wrapper in `App.tsx` has `overflow-hidden` which **clips** the content instead. The result: the left portion of the page is clipped and invisible.

Additionally, the page wrapper div uses `className="w-full flex justify-center py-3"` — when the `<Page>` canvas is wider than the container, `w-full` expands to match the scroll-width rather than the viewport-width, breaking centering.

**The fix:** Constrain the `<Page>` component to never exceed the available container width. Use the `width` prop on `<Page>` instead of relying on `scale` alone. Measure the scroll container's width using a `ResizeObserver` and pass it as the page width, then let scale act as a multiplier on top of that — OR use a simpler approach: compute `width = containerWidth * zoom` and pass that directly to `<Page>`, removing the `scale` prop.

The simplest correct implementation:

```tsx
// Measure the scroll container width
const [containerWidth, setContainerWidth] = useState(0);

useEffect(() => {
  const el = scrollContainerRef.current;
  if (!el) return;
  const ro = new ResizeObserver(() => {
    setContainerWidth(el.clientWidth);
  });
  ro.observe(el);
  return () => ro.disconnect();
}, []);

// In the Page render:
<Page
  pageNumber={pageNumber}
  width={containerWidth > 0 ? containerWidth * zoom : undefined}
  renderAnnotationLayer={true}
  renderTextLayer={true}
/>
```

Remove the `scale` prop entirely — using `width` is the correct API for responsive PDF rendering in react-pdf v9. The `scale` prop bypasses layout constraints; `width` respects them.

**Also update the zoom controls** to reflect that zoom is now a multiplier on container width (not on the PDF's intrinsic size):
- Keep the zoom range `0.6` to `2.5` as-is — these work as width multipliers
- The zoom display (`{Math.round(zoom * 100)}%`) remains correct — 100% = container width, 120% = slightly wider with horizontal scroll

---

## Implementation Steps

### Step 1: Add CSS imports

In `frontend/src/main.tsx`, add at the top after the existing imports:

```typescript
import 'react-pdf/dist/Page/TextLayer.css';
import 'react-pdf/dist/Page/AnnotationLayer.css';
```

These files ship with the `react-pdf` package already installed — no new dependencies needed.

### Step 2: Add container width measurement to `PdfViewer`

Add a new state variable and a `ResizeObserver` that watches `scrollContainerRef`:

```typescript
const [containerWidth, setContainerWidth] = useState(0);

useEffect(() => {
  const el = scrollContainerRef.current;
  if (!el) return;
  const ro = new ResizeObserver(entries => {
    const entry = entries[0];
    if (entry) setContainerWidth(entry.contentRect.width);
  });
  ro.observe(el);
  // Set initial value immediately
  setContainerWidth(el.clientWidth);
  return () => ro.disconnect();
}, []);
```

### Step 3: Replace `scale` with `width` on `<Page>`

Change this:
```tsx
<Page
  pageNumber={pageNumber}
  scale={zoom}
  renderAnnotationLayer={true}
  renderTextLayer={true}
/>
```

To this:
```tsx
<Page
  pageNumber={pageNumber}
  width={containerWidth > 0 ? Math.floor(containerWidth * zoom) : undefined}
  renderAnnotationLayer={true}
  renderTextLayer={true}
/>
```

The `Math.floor` prevents sub-pixel width values that can cause blurry rendering.

### Step 4: Add horizontal padding to account for scrollbar width

When `zoom > 1.0`, the page will be wider than the container and a horizontal scrollbar will appear. To prevent the page from being clipped by the scrollbar gutter, add horizontal padding to the scroll container:

Change the scroll container className from:
```
"flex-1 overflow-y-auto overflow-x-auto bg-slate-950"
```
To:
```
"flex-1 overflow-y-auto overflow-x-auto bg-slate-950 min-w-0"
```

And give each page wrapper some horizontal padding so the page doesn't touch the panel edge at default zoom:
```tsx
className="w-full flex justify-center py-3 px-2"
```

### Step 5: Update the zoom reset button

The Reset button currently resets to `1.2`. Since we're no longer using scale (where 1.2 = 120% of intrinsic size), reset to `1.0` (= 100% of container width, which fills the panel neatly):

```tsx
<button onClick={() => setZoom(1.0)}>Reset</button>
```

And update the initial zoom state:
```tsx
const [zoom, setZoom] = useState(1.0);
```

---

## Constraints — Do Not Change These

1. **Do not change the IntersectionObserver logic** — the multi-page scroll tracking, `programmaticScrollRef`, and `visiblePagesRef` are correct and should be untouched.

2. **Do not change the toolbar controls** (Prev/Next buttons, zoom +/−) except the Reset button default value as specified above.

3. **Do not change `pdfjs.GlobalWorkerOptions.workerSrc`** initialization.

4. **Do not change how `onLoadSuccess` updates `pdfNumPages`** — that logic is correct.

5. **Do not change `App.tsx`** — the `overflow-hidden` on the Panel wrapper div is intentional for the overall layout. The fix must be inside `PdfViewer.tsx` itself and the CSS imports.

6. **Do not add any new npm packages** — `react-pdf` already ships the CSS files, and `ResizeObserver` is a native browser API available in all modern browsers.

7. **Preserve the `containerWidth > 0` guard** — when the component first mounts, `containerWidth` is 0 and the `<Page>` would render at 0px wide. The guard `containerWidth > 0 ? Math.floor(containerWidth * zoom) : undefined` causes react-pdf to use its default sizing on first render, then re-render correctly once the ResizeObserver fires (which is nearly immediate).

---

## Files to Modify

| File | Change |
|------|--------|
| `frontend/src/main.tsx` | Add 2 CSS imports for TextLayer and AnnotationLayer |
| `frontend/src/components/DocumentViewer/PdfViewer.tsx` | Add `containerWidth` state + ResizeObserver, replace `scale` with `width` on `<Page>`, add `px-2` to page wrapper, reset zoom default to `1.0` |

**Do not modify any other files.**

---

## Validation Checklist

After implementing, verify:

- [ ] Text in the PDF is selectable and the highlight appears **on top of** the correct text, not floating elsewhere
- [ ] At default zoom (1.0), the full page width fits inside the panel with no horizontal scrollbar
- [ ] At zoom > 1.0, a horizontal scrollbar appears and the full page is accessible by scrolling (not clipped)
- [ ] Resizing the browser window or dragging the panel resize handle updates the page width dynamically (ResizeObserver fires)
- [ ] The page highlight indicator (amber bar for selected node) still appears correctly
- [ ] Prev/Next page navigation still works
- [ ] Multi-page scroll and IntersectionObserver-based page tracking still works
- [ ] No console errors about canvas size or worker initialization
