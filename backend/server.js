const express = require("express");
const cors = require("cors");
const mongoose = require("mongoose");
const path = require("path");
const dotenv = require("dotenv");
const agentRoutes = require("./routes/agent");
const orderRoutes = require("./routes/orders");
const paymentRoutes = require("./routes/payments");
const dashboardRoutes = require("./routes/dashboard");

dotenv.config({
    path: path.resolve(__dirname, "../.env")
});

const app = express();

app.use(cors());
app.use(express.json());
app.use("/api/agent", agentRoutes);
app.use("/api/orders", orderRoutes);
app.use("/api/payments", paymentRoutes);
app.use("/api/dashboard", dashboardRoutes);

app.get("/", (req, res) => {
    res.json({
        service: "MerchantOS Backend",
        status: "running"
    });
});

app.get("/health", (req, res) => {
    res.json({
        status: "healthy"
    });
});

const PORT = process.env.PORT || 5000;

mongoose
    .connect(process.env.MONGODB_URI)
    .then(() => {
        console.log("MongoDB Atlas connected successfully");

        app.listen(PORT, () => {
            console.log(`MerchantOS Backend running on port ${PORT}`);
        });
    })
    .catch((error) => {
        console.error("MongoDB connection failed:", error.message);
    });