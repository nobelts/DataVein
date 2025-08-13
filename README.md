# DataVein

**A modern data processing and augmentation platform that transforms small datasets into larger, statistically accurate training datasets.**

DataVein helps data scientists and ML engineers overcome the common challenge of insufficient training data by generating synthetic data that maintains the statistical properties and patterns of the original dataset.

## ✨ Features

- **Smart Data Augmentation**: Generate synthetic data using advanced statistical methods
- **Multiple Algorithms**: Noise injection, statistical sampling, and pattern-based generation
- **Format Flexibility**: Support for CSV, JSON, Excel, and Parquet files
- **Scalable Processing**: Handle datasets from hundreds to millions of records
- **Real-time Progress**: Track augmentation progress with detailed status updates
- **Secure Storage**: User-isolated data storage with enterprise-grade security
- **Export Options**: Download results in multiple formats for immediate use

## 🎯 Use Cases

- **Machine Learning**: Expand training datasets for better model performance
- **Data Testing**: Generate realistic test data for application development
- **Analytics**: Create larger samples for more robust statistical analysis
- **Privacy**: Generate synthetic data that preserves patterns without exposing sensitive information

## 🛠 Technology Stack

**Backend**
- FastAPI (Python) - High-performance async API
- PostgreSQL - Robust data persistence
- Redis - Fast caching and session management
- MinIO - S3-compatible object storage

**Frontend**
- React + TypeScript - Modern, type-safe UI
- Tailwind CSS - Responsive, utility-first styling
- Vite - Fast development and optimized builds

**Infrastructure**
- Docker - Containerized deployment
- JWT Authentication - Secure user management
- RESTful API - Clean, documented endpoints

## 🚀 Quick Demo

1. **Upload** your dataset (CSV, JSON, Excel)
2. **Configure** augmentation method and target size
3. **Generate** synthetic data while tracking progress
4. **Download** expanded dataset in your preferred format

## 🏗 Architecture

DataVein uses a microservices architecture with separate components for data processing, storage, and user management. The platform processes data asynchronously, allowing users to work with large datasets without blocking the interface.

## 📊 Why DataVein?

Traditional data augmentation often requires deep ML expertise and custom implementations. DataVein provides an intuitive interface for generating high-quality synthetic data that maintains statistical integrity while being accessible to users of all technical levels.

---

**[Setup Instructions](SETUP.md)** | **[API Documentation](http://localhost:8000/docs)** | **[License](LICENSE)**

## 🏗 Project Structure

```
root/
├── backend/           # FastAPI API server
├── frontend/          # React + TypeScript UI
├── worker/            # Async data processing
├── infra/             # Docker containers
├── scripts/           # Utilities & deployment
└── tests/             # Test suites
```

---

**[Setup Instructions](SETUP.md)** | **[API Documentation](http://localhost:8000/docs)** | **[License](LICENSE)**


## License
