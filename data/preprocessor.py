"""Data preprocessing and feature engineering."""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import logging
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FeatureEngineer:
    """Feature engineering for stock data."""
    
    @staticmethod
    def calculate_moving_averages(
        data: pd.DataFrame,
        windows: list = None
    ) -> pd.DataFrame:
        """Calculate moving averages."""
        if windows is None:
            windows = [10, 20, 50, 100, 200]
        
        for window in windows:
            data[f'MA_{window}'] = data['Close'].rolling(window).mean()
        
        return data
    
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Relative Strength Index."""
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        return data
    
    @staticmethod
    def calculate_macd(data: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD."""
        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
        
        data['MACD'] = exp1 - exp2
        data['MACD_Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
        data['MACD_Diff'] = data['MACD'] - data['MACD_Signal']
        
        return data
    
    @staticmethod
    def calculate_bollinger_bands(
        data: pd.DataFrame,
        period: int = 20,
        num_std: float = 2.0
    ) -> pd.DataFrame:
        """Calculate Bollinger Bands."""
        data['BB_Middle'] = data['Close'].rolling(window=period).mean()
        std = data['Close'].rolling(window=period).std()
        
        data['BB_Upper'] = data['BB_Middle'] + (std * num_std)
        data['BB_Lower'] = data['BB_Middle'] - (std * num_std)
        data['BB_Width'] = data['BB_Upper'] - data['BB_Lower']
        data['BB_Pct'] = (data['Close'] - data['BB_Lower']) / data['BB_Width']
        
        return data
    
    @staticmethod
    def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Average True Range."""
        data['TR'] = np.maximum(
            data['High'] - data['Low'],
            np.maximum(
                abs(data['High'] - data['Close'].shift(1)),
                abs(data['Low'] - data['Close'].shift(1))
            )
        )
        
        data['ATR'] = data['TR'].rolling(window=period).mean()
        
        return data
    
    @staticmethod
    def calculate_volume_features(data: pd.DataFrame) -> pd.DataFrame:
        """Calculate volume-based features."""
        data['Volume_MA'] = data['Volume'].rolling(window=20).mean()
        data['Volume_Ratio'] = data['Volume'] / data['Volume_MA']
        
        # On-Balance Volume
        obv = np.where(data['Close'] > data['Close'].shift(1),
                       data['Volume'],
                       np.where(data['Close'] < data['Close'].shift(1),
                               -data['Volume'],
                               0))
        data['OBV'] = np.cumsum(obv)
        
        return data
    
    @staticmethod
    def calculate_returns(data: pd.DataFrame) -> pd.DataFrame:
        """Calculate returns."""
        data['Returns'] = data['Close'].pct_change()
        data['Log_Returns'] = np.log(data['Close'] / data['Close'].shift(1))
        data['Cumulative_Returns'] = (1 + data['Returns']).cumprod()
        
        return data
    
    @staticmethod
    def calculate_volatility(data: pd.DataFrame, period: int = 30) -> pd.DataFrame:
        """Calculate volatility metrics."""
        data['Volatility'] = data['Returns'].rolling(window=period).std()
        data['Volatility_MA'] = data['Volatility'].rolling(window=period).mean()
        
        return data


class DataPreprocessor:
    """Main data preprocessing pipeline."""
    
    def __init__(self):
        """Initialize preprocessor."""
        self.scaler = MinMaxScaler()
        self.feature_engineer = FeatureEngineer()
        
    def preprocess(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Full preprocessing pipeline."""
        logger.info("Starting data preprocessing")
        
        # Drop duplicates
        data = data[~data.index.duplicated(keep='first')]
        
        # Feature engineering
        data = self.feature_engineer.calculate_moving_averages(data)
        data = self.feature_engineer.calculate_rsi(data)
        data = self.feature_engineer.calculate_macd(data)
        data = self.feature_engineer.calculate_bollinger_bands(data)
        data = self.feature_engineer.calculate_atr(data)
        data = self.feature_engineer.calculate_volume_features(data)
        data = self.feature_engineer.calculate_returns(data)
        data = self.feature_engineer.calculate_volatility(data)
        
        # Drop NaN values
        data = data.dropna()
        
        # Normalize features
        feature_cols = [col for col in data.columns if col != 'Volume']
        scaled_data = self.scaler.fit_transform(data[feature_cols])
        data_scaled = pd.DataFrame(scaled_data, columns=feature_cols, index=data.index)
        
        metadata = {
            'original_shape': data.shape,
            'feature_count': len(feature_cols),
            'date_range': (data.index[0], data.index[-1]),
            'scaler': self.scaler,
            'features': feature_cols
        }
        
        logger.info(f"Preprocessing complete. Shape: {data_scaled.shape}")
        
        return data_scaled, metadata


def create_sequences(
    data: np.ndarray,
    seq_length: int = 60
) -> Tuple[np.ndarray, np.ndarray]:
    """Create sequences for time-series models."""
    X, y = [], []
    
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length, 0])
    
    return np.array(X), np.array(y)