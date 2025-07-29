#!/usr/bin/env python3
"""
Memory Optimization for Render Deployment
Disables memory-intensive features to reduce memory usage
"""

import os
from logger import logger

class MemoryOptimizer:
    """Optimizes memory usage for deployment environments"""
    
    def __init__(self):
        self.memory_limit_mb = int(os.getenv('MEMORY_LIMIT_MB', '512'))
        self.enable_intelligent_memory = os.getenv('ENABLE_INTELLIGENT_MEMORY', 'false').lower() == 'true'
        self.enable_deep_learning = os.getenv('ENABLE_DEEP_LEARNING', 'false').lower() == 'true'
        self.enable_advanced_caching = os.getenv('ENABLE_ADVANCED_CACHING', 'true').lower() == 'true'
        
        logger.info(f"Memory optimizer initialized: limit={self.memory_limit_mb}MB")
        logger.info(f"Intelligent memory: {self.enable_intelligent_memory}")
        logger.info(f"Deep learning: {self.enable_deep_learning}")
        logger.info(f"Advanced caching: {self.enable_advanced_caching}")
    
    def should_enable_intelligent_memory(self) -> bool:
        """Check if intelligent memory should be enabled"""
        return self.enable_intelligent_memory and self.memory_limit_mb > 256
    
    def should_enable_deep_learning(self) -> bool:
        """Check if deep learning features should be enabled"""
        return self.enable_deep_learning and self.memory_limit_mb > 512
    
    def should_enable_advanced_caching(self) -> bool:
        """Check if advanced caching should be enabled"""
        return self.enable_advanced_caching
    
    def get_cache_size_limit(self) -> int:
        """Get appropriate cache size based on memory limit"""
        if self.memory_limit_mb <= 256:
            return 100
        elif self.memory_limit_mb <= 512:
            return 500
        else:
            return 1000
    
    def get_connection_pool_size(self) -> int:
        """Get appropriate connection pool size"""
        if self.memory_limit_mb <= 256:
            return 5
        elif self.memory_limit_mb <= 512:
            return 10
        else:
            return 20
    
    def optimize_for_render(self):
        """Apply Render-specific optimizations"""
        logger.info("Applying Render deployment optimizations...")
        
        # Set environment variables for memory optimization
        os.environ['ENABLE_INTELLIGENT_MEMORY'] = 'false'
        os.environ['ENABLE_DEEP_LEARNING'] = 'false'
        os.environ['ENABLE_ADVANCED_CACHING'] = 'true'
        os.environ['MEMORY_LIMIT_MB'] = '512'
        
        logger.info("Render optimizations applied")

# Global instance
memory_optimizer = MemoryOptimizer()

# Apply Render optimizations if running on Render
if os.getenv('RENDER'):
    memory_optimizer.optimize_for_render()