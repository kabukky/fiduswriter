import {Plugin, PluginKey} from "prosemirror-state"
import {READ_ONLY_ROLES, COMMENT_ONLY_ROLES} from ".."

const key = new PluginKey('accessRights')

export let accessRightsPlugin = function(options) {
    return new Plugin({
        key,
        filterTransaction: (tr, state) => {
            let allowed = true
            let remote = tr.getMeta('remote')
            if (remote) {
                return allowed
            }

            if (READ_ONLY_ROLES.includes(options.editor.docInfo.access_rights)) {
                // User only has read access. Don't allow anything.
                allowed = false
            } else if (COMMENT_ONLY_ROLES.includes(options.editor.docInfo.access_rights)) {
                //User has a comment-only role (commentator, editor or reviewer)

                //Check all transaction steps. If step type not allowed = prohibit
                //check if in allowed array. if false - exit loop
                if (!tr.steps.every(step =>
                    (step.jsonID === 'addMark' || step.jsonID === 'removeMark') &&
                    step.mark.type.name === 'comment'
                )) {
                    allowed = false
                }
            }

            return allowed
        }
    })
}
