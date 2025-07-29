"""
Binance ticker price tool implementation.

This module provides functionality to fetch current price data for trading symbols
from the Binance exchange API.
"""

import time
import logging
from typing import Dict, Any
from binance.exceptions import BinanceAPIException, BinanceRequestException
from binance_mcp_server.utils import (
    get_binance_client, 
    create_error_response, 
    create_success_response,
    rate_limited,
    binance_rate_limiter
)

logger = logging.getLogger(__name__)


def validate_symbol(symbol: str) -> str:
    """
    Validate and normalize trading symbol format.
    
    Args:
        symbol: Trading pair symbol to validate
        
    Returns:
        str: Normalized symbol in uppercase
        
    Raises:
        ValueError: If symbol format is invalid
    """
    if not symbol or not isinstance(symbol, str):
        raise ValueError("Symbol must be a non-empty string")
    
    # Normalize symbol format
    symbol = symbol.upper().strip()
    
    # Basic validation
    if len(symbol) < 3:
        raise ValueError("Symbol must be at least 3 characters long")
        
    if not symbol.isalnum():
        raise ValueError("Symbol must contain only alphanumeric characters")
    
    return symbol


@rate_limited(binance_rate_limiter)
def get_ticker_price(symbol: str) -> Dict[str, Any]:
    """
    Get the current price for a trading symbol on Binance.
    
    This function fetches real-time price data for any valid trading pair available
    on Binance. The price is returned in the quote currency of the pair.
    
    Args:
        symbol: Trading pair symbol in format BASEQUOTE (e.g., 'BTCUSDT', 'ETHBTC')
            Must be a valid symbol listed on Binance exchange.
        
    Returns:
        Dict containing:
        - success (bool): Whether the request was successful
        - data (dict): Response data containing symbol, price, and timestamp
        - timestamp (int): Unix timestamp of the response
        - error (dict, optional): Error details if request failed
        
    Examples:
        result = get_ticker_price("BTCUSDT")  # Bitcoin price in USDT
        if result["success"]:
            price = result["data"]["price"]
            print(f"BTC price: ${price}")
    """
    logger.info(f"Fetching ticker price for symbol: {symbol}")
    
    try:
        normalized_symbol = validate_symbol(symbol)
        
        client = get_binance_client()
        
        ticker_data = client.get_symbol_ticker(symbol=normalized_symbol)
        
        response_data = {
            "symbol": ticker_data["symbol"],
            "price": float(ticker_data["price"])
        }
        
        logger.info(f"Successfully fetched price for {normalized_symbol}: {response_data['price']}")
        
        return create_success_response(
            data=response_data,
            metadata={
                "source": "binance_api",
                "endpoint": "ticker_price"
            }
        )
        
    except ValueError as e:
        error_msg = f"Invalid symbol format: {str(e)}"
        logger.warning(f"Validation error for symbol '{symbol}': {error_msg}")
        return create_error_response("validation_error", error_msg)
        
    except BinanceAPIException as e:
        error_msg = f"Binance API error: {e.message}"
        logger.error(f"API error for symbol '{symbol}': {error_msg}")
        return create_error_response("api_error", error_msg, {"code": e.code})
        
    except BinanceRequestException as e:
        error_msg = f"Network error: {str(e)}"
        logger.error(f"Network error for symbol '{symbol}': {error_msg}")
        return create_error_response("network_error", error_msg)
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected error for symbol '{symbol}': {error_msg}")
        return create_error_response("internal_error", error_msg)