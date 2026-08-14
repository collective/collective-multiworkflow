/**
 * SHADOWED from @plone/volto 19.3.0
 * `src/components/manage/Workflow/Workflow.jsx`.
 *
 * Kept deliberately close to upstream so a Volto upgrade is a small diff:
 * re-copy the original and re-apply the two blocks marked
 * `--- collective.multiworkflow ---`.
 *
 * What changes: the control renders one selector per workflow in the object's
 * chain instead of only the publication workflow. With no additional workflows
 * — which is every object on a site without this add-on — the extra block
 * renders nothing and the component behaves exactly as upstream.
 *
 * This is also the shape the eventual core change would take, so treat this
 * file as the prototype of that patch.
 */

export { default } from '@plone-collective/volto-multiworkflow/components/Workflow/Workflow';
