/**
 * SHADOWED from @plone/volto 19.3.0
 * `src/components/manage/History/History.jsx`.
 *
 * Kept deliberately close to upstream so a Volto upgrade is a small diff:
 * re-copy the original and re-apply the three blocks marked
 * `--- collective.multiworkflow ---`.
 *
 * What changes: upstream reads each entry's previous state off the entry
 * before it in the list, which only holds while a history describes a single
 * workflow. `@history` merges the whole chain into one stream, so that read
 * invents transitions between unrelated workflows. Threading is done per
 * `workflow_id` instead, and a history spanning several workflows names the
 * workflow on every row.
 *
 * With no additional workflows — which is every object on a site without this
 * add-on — the threading reduces to upstream's and the extra column is not
 * rendered, so the table is byte-for-byte the one Plone has always shown.
 *
 * This is also the shape the eventual core change would take, so treat this
 * file as the prototype of that patch.
 */

export { default } from '@plone-collective/volto-multiworkflow/components/History/History';
