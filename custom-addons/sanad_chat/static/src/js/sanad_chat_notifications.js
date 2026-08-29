/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

/**
 * SANAD Chat real-time notifications.
 *
 * Subscribes to the current user's private bus.bus channel and shows a
 * desktop-style notification whenever a new message is posted on a
 * sanad.chat.conversation the user participates in. mail.thread already
 * pushes messages over bus.bus to followers automatically (Odoo 19 core
 * behavior) - this service only adds a SANAD-specific toast so chat
 * activity is visible even outside the Discuss/Chat view, per the PRD's
 * notification requirement (Section 17: "Doctor message" / patient
 * message events).
 */
const sanadChatNotificationService = {
    dependencies: ["bus_service", "notification"],

    start(env, { bus_service, notification }) {
        bus_service.subscribe("mail.message/insert", (payload) => {
            const messages = Array.isArray(payload) ? payload : [payload];
            for (const message of messages) {
                if (message?.model === "sanad.chat.conversation") {
                    notification.add(
                        message.body_preview || _t("You have a new message."),
                        {
                            title: _t("SANAD - New Message"),
                            type: "info",
                        }
                    );
                }
            }
        });
        bus_service.start();
    },
};

registry.category("services").add("sanadChatNotifications", sanadChatNotificationService);
