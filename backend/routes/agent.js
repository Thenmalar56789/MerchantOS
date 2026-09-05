const express = require("express");
const axios = require("axios");

const PurchaseIntent =
    require("../models/PurchaseIntent");

const router = express.Router();

router.post("/recommend", async (req, res) => {
    try {
        const { message } = req.body;

        if (!message) {
            return res.status(400).json({
                success: false,
                message: "Customer message is required"
            });
        }

        // Send customer request to AI service
        const response = await axios.post(
            "http://127.0.0.1:8000/agent/recommend",
            {
                message
            }
        );

        const aiResult = response.data;

        /*
         * A purchase intent is considered:
         *
         * created       -> valid purchase opportunity
         * not_converted -> blocked/rejected request
         *
         * It becomes "converted" only after successful
         * Razorpay payment verification.
         */

        const intentStatus =
            aiResult.canPurchase
                ? "created"
                : "not_converted";

        const purchaseIntent =
            await PurchaseIntent.create({
                customerMessage: message,

                productRequested:
                    aiResult.intent?.product || null,

                maxPrice:
                    aiResult.intent?.maxPrice ?? null,

                minPrice:
                    aiResult.intent?.minPrice ?? null,

                requirements:
                    aiResult.intent?.requirements || [],

                status:
                    intentStatus
            });

        console.log(
            "Purchase intent created:",
            purchaseIntent._id.toString(),
            "| status:",
            intentStatus
        );

        res.json({
            success: true,

            response:
                aiResult.response,

            canPurchase:
                aiResult.canPurchase,

            stage:
                aiResult.stage,

            intent:
                aiResult.intent,

            product:
                aiResult.product,

            offer:
                aiResult.offer,

            decision:
                aiResult.decision,

            verification:
                aiResult.verification,

            intentId:
                purchaseIntent._id
        });

    } catch (error) {

        console.error(
            "AI service error:",
            error.response?.data ||
            error.message
        );

        res.status(500).json({
            success: false,
            message:
                "AI service unavailable"
        });
    }
});

module.exports = router;