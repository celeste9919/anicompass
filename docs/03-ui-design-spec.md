# UI And Interaction Design Specification

## Product Character

AniCompass should feel light, clear, friendly, and focused on repeated use. It
is an application workspace, not a marketing landing page.

## First View

The first window must immediately show the AniCompass name, recommendation
controls, a clear recommendation action, navigation to Search, My List,
History, and Settings, plus current language and theme controls.

## Navigation

Use a stable desktop sidebar or compact rail:

1. Recommend
2. Search
3. My List
4. History
5. Settings

Navigation dimensions must remain stable when labels change language.

## Recommendation Screen

- Use grouped form sections, not nested cards.
- Use chips or checkboxes for genres, mood, region, and avoidance tags.
- Use a segmented control for recommendation count: 3 / 5 / 10.
- Use a clear text area for natural-language preferences.
- Use compact token inputs for liked and disliked titles.
- Disable duplicate submission while a request is active.
- Provide a visible cancel action for long requests.

## Result Cards

Each repeated result may use one compact card with a readable cover, localized
title, original title, essential metadata, recommendation reason, content
warnings, and one list-status action.

Cards must not contain nested cards. Missing cover art uses a neutral branded
placeholder that does not imitate a real title.

## Watch List

- Use tabs or a segmented control for Plan to watch, Watching, and Completed.
- Support search and sorting.
- Episode progress uses a numeric stepper or input.
- Score uses a stable 1-10 control.
- Notes open in a focused editor panel or dialog.
- Deletion requires confirmation and supports cancellation.

## Theme System

- Provide a color picker and accessible starter swatches.
- Derive accent, hover, focus, selected, and subtle background colors from the
  chosen accent.
- Do not recolor every surface into one hue.
- Keep neutral backgrounds and semantic colors for success, warning, and error.
- Validate text and control contrast after theme changes.

## Language

- All visible strings come from translation resources.
- Do not concatenate translated fragments.
- Account for Chinese and English length differences.
- Use localized display titles while retaining the original title.

## Required States

Every network-backed surface has empty, loading, success, partial success, no
result, offline, timeout, rate limited, configuration missing, and recoverable
error states. No state may use fabricated anime or AI results.

## Accessibility And Ergonomics

- Keyboard navigation for primary controls.
- Visible focus indicators.
- Tooltips for unfamiliar icons.
- Practical click targets.
- Text wraps without overlapping controls.
- Animation is restrained and optional.
- Status is never conveyed by color alone.

## Responsive Desktop Constraints

Support a practical minimum window size and define minimum widths for sidebar,
form, and result content. Narrow windows may stack form and results, but must
not hide actions or allow text overlap.

