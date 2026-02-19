"""
Application Entry Point
Main entry point for the Order Management System.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Order Management System",
    description="A Hexagonal Architecture-based order management system",
    version="0.1.0",
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Order Management System API"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
