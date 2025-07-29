// Pricing utilities for Claude API cost calculations
// This is the frontend version of the pricing module

// Dynamic pricing cache
let DYNAMIC_PRICING = null;
let PRICING_LOAD_ATTEMPTED = false;
let PRICING_LOAD_ERROR = null;

// Default pricing in USD per token (not per million)
// Based on Anthropic's public pricing
const DEFAULT_CLAUDE_PRICING = {
  'claude-opus-4-20250514': {
    'input_cost_per_token': 15.0 / 1_000_000,  // $15 per million
    'output_cost_per_token': 75.0 / 1_000_000,  // $75 per million
    'cache_creation_cost_per_token': 18.75 / 1_000_000,  // $18.75 per million
    'cache_read_cost_per_token': 1.50 / 1_000_000  // $1.50 per million
  },
  'claude-3-5-sonnet-20241022': {
    'input_cost_per_token': 3.0 / 1_000_000,  // $3 per million
    'output_cost_per_token': 15.0 / 1_000_000,  // $15 per million
    'cache_creation_cost_per_token': 3.75 / 1_000_000,  // $3.75 per million
    'cache_read_cost_per_token': 0.30 / 1_000_000  // $0.30 per million
  },
  'claude-3-5-haiku-20241022': {
    'input_cost_per_token': 1.0 / 1_000_000,  // $1 per million
    'output_cost_per_token': 5.0 / 1_000_000,  // $5 per million
    'cache_creation_cost_per_token': 1.25 / 1_000_000,  // $1.25 per million
    'cache_read_cost_per_token': 0.10 / 1_000_000  // $0.10 per million
  },
  'claude-3-opus-20240229': {
    'input_cost_per_token': 15.0 / 1_000_000,  // $15 per million
    'output_cost_per_token': 75.0 / 1_000_000,  // $75 per million
    'cache_creation_cost_per_token': 18.75 / 1_000_000,  // $18.75 per million
    'cache_read_cost_per_token': 1.50 / 1_000_000  // $1.50 per million
  },
  'claude-3-sonnet-20240229': {
    'input_cost_per_token': 3.0 / 1_000_000,  // $3 per million
    'output_cost_per_token': 15.0 / 1_000_000,  // $15 per million
    'cache_creation_cost_per_token': 3.75 / 1_000_000,  // $3.75 per million
    'cache_read_cost_per_token': 0.30 / 1_000_000  // $0.30 per million
  },
  'claude-3-haiku-20240307': {
    'input_cost_per_token': 0.25 / 1_000_000,  // $0.25 per million
    'output_cost_per_token': 1.25 / 1_000_000,  // $1.25 per million
    'cache_creation_cost_per_token': 0.30 / 1_000_000,  // $0.30 per million
    'cache_read_cost_per_token': 0.03 / 1_000_000  // $0.03 per million
  }
};

// Load dynamic pricing from API
async function loadDynamicPricing() {
  if (PRICING_LOAD_ATTEMPTED) {
    return DYNAMIC_PRICING !== null;
  }
    
  PRICING_LOAD_ATTEMPTED = true;
    
  try {
    const response = await fetch('/api/pricing');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
        
    const data = await response.json();
        
    if (data.error) {
      throw new Error(data.error);
    }
        
    DYNAMIC_PRICING = data.pricing;
        
    // Log the pricing source
    if (data.source === 'cache') {
      console.log('Model pricing loaded from cache', data.is_stale ? '(stale)' : '(fresh)');
    } else if (data.source === 'litellm') {
      console.log('Model pricing loaded from LiteLLM');
    } else if (data.source === 'default') {
      console.log('Model pricing loaded from default values set in pricing.js');
    }
        
    // Show warning if pricing is stale
    if (data.is_stale) {
      console.warn('Using stale pricing data from cache');
    }
        
    return true;
  } catch (error) {
    console.error('Failed to load dynamic pricing:', error);
    console.log('Will use default values from pricing.js as fallback');
    PRICING_LOAD_ERROR = error.message;
    return false;
  }
}

// Force refresh pricing
async function refreshPricing() {
  try {
    const response = await fetch('/api/pricing/refresh', { method: 'POST' });
    const data = await response.json();
        
    if (data.status === 'success') {
      // Reload the pricing
      PRICING_LOAD_ATTEMPTED = false;
      DYNAMIC_PRICING = null;
      return await loadDynamicPricing();
    }
        
    return false;
  } catch (error) {
    console.error('Failed to refresh pricing:', error);
    return false;
  }
}

// Check if pricing is available
function isPricingAvailable() {
  return DYNAMIC_PRICING !== null || DEFAULT_CLAUDE_PRICING !== null;
}

// Get error message if pricing failed to load
function getPricingError() {
  if (!PRICING_LOAD_ATTEMPTED) {
    return null;
  }
    
  if (DYNAMIC_PRICING === null && !navigator.onLine) {
    return 'Model prices can\'t be fetched - no internet connection';
  }
    
  return PRICING_LOAD_ERROR;
}

function getModelPricing(modelName) {
  // First try dynamic pricing
  if (DYNAMIC_PRICING && modelName in DYNAMIC_PRICING) {
    return DYNAMIC_PRICING[modelName];
  }
    
  // Then try default pricing
  // Direct match
  if (modelName in DEFAULT_CLAUDE_PRICING) {
    return DEFAULT_CLAUDE_PRICING[modelName];
  }
    
  // Try to match by partial name (e.g., "claude-3-5-sonnet" without date)
  for (const [knownModel, pricing] of Object.entries(DEFAULT_CLAUDE_PRICING)) {
    if (modelName.includes(knownModel) || knownModel.includes(modelName)) {
      return pricing;
    }
  }
    
  // Default to Sonnet pricing if model not recognized
  return DEFAULT_CLAUDE_PRICING['claude-3-5-sonnet-20241022'];
}

function calculateCost(tokens, model) {
  const pricing = getModelPricing(model);
  if (!pricing) {
    return {
      input_cost: 0.0,
      output_cost: 0.0,
      cache_creation_cost: 0.0,
      cache_read_cost: 0.0,
      total_cost: 0.0
    };
  }
    
  const costs = {
    input_cost: (tokens.input || 0) * pricing.input_cost_per_token,
    output_cost: (tokens.output || 0) * pricing.output_cost_per_token,
    cache_creation_cost: (tokens.cache_creation || 0) * pricing.cache_creation_cost_per_token,
    cache_read_cost: (tokens.cache_read || 0) * pricing.cache_read_cost_per_token
  };
    
  costs.total_cost = costs.input_cost + costs.output_cost + costs.cache_creation_cost + costs.cache_read_cost;
  return costs;
}

function formatCost(cost) {
  if (cost < 0.01) {
    return `$${cost.toFixed(4)}`;
  } else if (cost < 1) {
    return `$${cost.toFixed(3)}`;
  } else {
    return `$${cost.toFixed(2)}`;
  }
}

// Export pricing utilities
const PricingUtils = {
  DEFAULT_CLAUDE_PRICING,
  getModelPricing,
  calculateCost,
  formatCost,
  loadDynamicPricing,
  refreshPricing,
  isPricingAvailable,
  getPricingError
};

// Make available globally for browser usage
if (typeof window !== 'undefined') {
  window.PricingUtils = PricingUtils;
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PricingUtils;
}