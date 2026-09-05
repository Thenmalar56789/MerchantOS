const express = require("express");

const Order = require("../models/Order");
const Product = require("../models/Product");
const AgentDecision = require("../models/AgentDecision");
const AuditLog = require("../models/AuditLog");
const PurchaseIntent =
    require("../models/PurchaseIntent");

const router = express.Router();

router.get("/metrics", async (req, res) => {
    try {
        // Get all completed/paid orders
        const paidOrders = await Order.find({
            paymentStatus: "paid"
        }).populate("productId");

        // Revenue
        const revenueGenerated = paidOrders.reduce(
            (total, order) =>
                total + order.finalAmount,
            0
        );

        // AI-assisted revenue
        const aiAssistedOrders =
            paidOrders.filter(
                order => order.aiAssisted
            );

        const aiAssistedRevenue =
            aiAssistedOrders.reduce(
                (total, order) =>
                    total + order.finalAmount,
                0
            );

        // Total discounts
        const discountGiven =
            paidOrders.reduce(
                (total, order) =>
                    total + order.discountAmount,
                0
            );

        // Estimated gross profit
        const estimatedProfit =
            paidOrders.reduce(
                (total, order) => {

                    const cost =
                        order.productId?.costPrice || 0;

                    const profit =
                        order.finalAmount - cost;

                    return total + profit;
                },
                0
            );

        // Average Order Value
        const averageOrderValue =
            paidOrders.length > 0
                ? revenueGenerated /
                  paidOrders.length
                : 0;

        // Orders
        const totalOrders =
            paidOrders.length;

        // AI-assisted orders
        const aiAssistedOrderCount =
            aiAssistedOrders.length;

        // Agent decisions
        const totalDecisions =
            await AgentDecision.countDocuments();

        const rejectedDecisions =
            await AgentDecision.countDocuments({
                decision: "reject"
            });

        const escalatedDecisions =
            await AgentDecision.countDocuments({
                decision: "escalate"
            });

        const clarifiedDecisions =
            await AgentDecision.countDocuments({
                decision: "clarify"
            });

        // Audit events
        const totalAuditEvents =
            await AuditLog.countDocuments();

        const totalPurchaseIntents =
    await PurchaseIntent.countDocuments();

const convertedPurchaseIntents =
    await PurchaseIntent.countDocuments({
        status: "converted"
    });

const conversionRate =
    totalPurchaseIntents > 0
        ? (
            convertedPurchaseIntents /
            totalPurchaseIntents
        ) * 100
        : 0;

        res.json({
            success: true,

            metrics: {
                revenueGenerated:
                    Number(
                        revenueGenerated.toFixed(2)
                    ),

                aiAssistedRevenue:
                    Number(
                        aiAssistedRevenue.toFixed(2)
                    ),

                discountGiven:
                    Number(
                        discountGiven.toFixed(2)
                    ),

                estimatedProfit:
                    Number(
                        estimatedProfit.toFixed(2)
                    ),

                averageOrderValue:
                    Number(
                        averageOrderValue.toFixed(2)
                    ),

                purchaseIntents:
    totalPurchaseIntents,

convertedIntents:
    convertedPurchaseIntents,

conversionRate:
    Number(
        conversionRate.toFixed(2)
    ),

                totalOrders,

                aiAssistedOrders:
                    aiAssistedOrderCount,

                totalAgentDecisions:
                    totalDecisions,

                blockedActions:
                    rejectedDecisions,

                escalatedActions:
                    escalatedDecisions,

                clarificationActions:
                    clarifiedDecisions,

                totalAuditEvents
            }
        });

    } catch (error) {

        console.error(
            "Dashboard metrics error:",
            error.message
        );

        res.status(500).json({
            success: false,
            message:
                "Failed to load dashboard metrics"
        });
    }
});

module.exports = router;