"""
OLS regression implementation with comprehensive features
"""

from typing import Optional, Union, Dict, Any, List
import pandas as pd
import numpy as np
from scipy import stats
import warnings

from ..core.base import BaseModel, BaseEstimator
from ..core.results import EconometricResults
from ..core.utils import parse_formula, create_design_matrices, prepare_data


class OLSEstimator(BaseEstimator):
    """
    Ordinary Least Squares estimator with robust standard errors
    """
    
    def estimate(
        self,
        y: np.ndarray,
        X: np.ndarray,
        robust: str = 'nonrobust',
        cluster: Optional[pd.Series] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Estimate OLS parameters
        
        Parameters
        ----------
        y : np.ndarray
            Dependent variable
        X : np.ndarray
            Independent variables (including constant if desired)
        robust : str, default 'nonrobust'
            Type of standard errors ('nonrobust', 'hc0', 'hc1', 'hc2', 'hc3', 'hac')
        cluster : pd.Series, optional
            Cluster variable for clustered standard errors
        **kwargs
            Additional options
            
        Returns
        -------
        Dict[str, Any]
            Estimation results
        """
        n, k = X.shape
        
        # OLS estimation
        try:
            XtX_inv = np.linalg.inv(X.T @ X)
        except np.linalg.LinAlgError:
            # Use pseudo-inverse if X'X is singular
            XtX_inv = np.linalg.pinv(X.T @ X)
            warnings.warn("X'X matrix is singular, using pseudo-inverse")
        
        params = XtX_inv @ X.T @ y
        fitted_values = X @ params
        residuals = y - fitted_values
        
        # Calculate standard errors
        if robust == 'nonrobust':
            # Classical standard errors
            sigma2 = np.sum(residuals**2) / (n - k)
            var_cov = sigma2 * XtX_inv
        elif robust.lower() in ['hc0', 'hc1', 'hc2', 'hc3']:
            # Heteroskedasticity-robust standard errors
            var_cov = self._robust_cov_matrix(X, residuals, XtX_inv, robust.lower())
        elif robust.lower() == 'hac':
            # HAC (Newey-West) standard errors
            var_cov = self._hac_cov_matrix(X, residuals, XtX_inv, **kwargs)
        elif cluster is not None:
            # Clustered standard errors
            var_cov = self._cluster_cov_matrix(X, residuals, XtX_inv, cluster)
        else:
            raise ValueError(f"Unknown robust option: {robust}")
        
        std_errors = np.sqrt(np.diag(var_cov))
        
        # Model diagnostics
        tss = np.sum((y - np.mean(y))**2)
        rss = np.sum(residuals**2)
        r_squared = 1 - rss / tss
        adj_r_squared = 1 - (rss / (n - k)) / (tss / (n - 1))
        
        # F-statistic (assuming constant in first column)
        if k > 1:
            r_squared_restricted = 0  # R² from constant-only model
            f_stat = ((r_squared - r_squared_restricted) / (k - 1)) / ((1 - r_squared) / (n - k))
            f_pvalue = 1 - stats.f.cdf(f_stat, k - 1, n - k)
        else:
            f_stat = f_pvalue = np.nan
        
        return {
            'params': params,
            'std_errors': std_errors,
            'var_cov': var_cov,
            'fitted_values': fitted_values,
            'residuals': residuals,
            'r_squared': r_squared,
            'adj_r_squared': adj_r_squared,
            'f_statistic': f_stat,
            'f_pvalue': f_pvalue,
            'nobs': n,
            'df_model': k - 1,
            'df_resid': n - k,
            'rss': rss,
            'tss': tss
        }
    
    def _robust_cov_matrix(
        self,
        X: np.ndarray,
        residuals: np.ndarray,
        XtX_inv: np.ndarray,
        robust_type: str
    ) -> np.ndarray:
        """Calculate heteroskedasticity-robust covariance matrix"""
        n, k = X.shape
        
        if robust_type == 'hc0':
            # White (1980)
            weights = residuals**2
        elif robust_type == 'hc1':
            # Degree of freedom correction
            weights = (n / (n - k)) * residuals**2
        elif robust_type == 'hc2':
            # MacKinnon and White (1985)
            h = np.diag(X @ XtX_inv @ X.T)
            weights = residuals**2 / (1 - h)
        elif robust_type == 'hc3':
            # Davidson and MacKinnon (1993)
            h = np.diag(X @ XtX_inv @ X.T)
            weights = residuals**2 / (1 - h)**2
        
        # Sandwich estimator
        meat = X.T @ np.diag(weights) @ X
        return XtX_inv @ meat @ XtX_inv
    
    def _hac_cov_matrix(
        self,
        X: np.ndarray,
        residuals: np.ndarray,
        XtX_inv: np.ndarray,
        lags: Optional[int] = None
    ) -> np.ndarray:
        """Calculate HAC (Newey-West) covariance matrix"""
        n, k = X.shape
        
        if lags is None:
            # Automatic lag selection (Newey-West rule)
            lags = int(np.floor(4 * (n / 100)**(2/9)))
        
        # Calculate centered moments
        moments = X * residuals[:, np.newaxis]
        
        # Gamma_0 (contemporaneous covariance)
        gamma_0 = moments.T @ moments / n
        
        # Gamma_j for j = 1, ..., lags
        gamma_sum = gamma_0.copy()
        for j in range(1, lags + 1):
            gamma_j = moments[j:].T @ moments[:-j] / n
            weight = 1 - j / (lags + 1)  # Bartlett kernel
            gamma_sum += weight * (gamma_j + gamma_j.T)
        
        return XtX_inv @ gamma_sum @ XtX_inv
    
    def _cluster_cov_matrix(
        self,
        X: np.ndarray,
        residuals: np.ndarray,
        XtX_inv: np.ndarray,
        cluster: pd.Series
    ) -> np.ndarray:
        """Calculate clustered standard errors"""
        n, k = X.shape
        
        # Get unique clusters
        clusters = cluster.unique()
        n_clusters = len(clusters)
        
        # Calculate cluster sum of moments
        meat = np.zeros((k, k))
        for cluster_id in clusters:
            cluster_idx = cluster == cluster_id
            X_c = X[cluster_idx]
            resid_c = residuals[cluster_idx]
            moments_c = (X_c * resid_c[:, np.newaxis]).sum(axis=0)
            meat += np.outer(moments_c, moments_c)
        
        # Finite sample correction
        correction = (n_clusters / (n_clusters - 1)) * ((n - 1) / (n - k))
        
        return correction * XtX_inv @ meat @ XtX_inv


class OLSRegression(BaseModel):
    """
    OLS regression model with comprehensive functionality
    """
    
    def __init__(
        self,
        formula: Optional[str] = None,
        data: Optional[pd.DataFrame] = None,
        y: Optional[np.ndarray] = None,
        X: Optional[np.ndarray] = None,
        var_names: Optional[List[str]] = None
    ):
        """
        Initialize OLS regression
        
        Parameters
        ----------
        formula : str, optional
            Regression formula (e.g., "y ~ x1 + x2")
        data : pd.DataFrame, optional
            Data containing variables
        y : np.ndarray, optional
            Dependent variable (alternative to formula)
        X : np.ndarray, optional
            Independent variables (alternative to formula)
        var_names : List[str], optional
            Variable names when using y, X directly
        """
        super().__init__()
        
        self.formula = formula
        self.data = data
        self.y = y
        self.X = X
        self.var_names = var_names
        self.estimator = OLSEstimator()
        
    def fit(
        self,
        robust: str = 'nonrobust',
        cluster: Optional[str] = None,
        **kwargs
    ) -> EconometricResults:
        """
        Fit the OLS model
        
        Parameters
        ----------
        robust : str, default 'nonrobust'
            Type of standard errors
        cluster : str, optional
            Variable name for clustering
        **kwargs
            Additional options
            
        Returns
        -------
        EconometricResults
            Fitted model results
        """
        # Prepare data
        if self.formula is not None and self.data is not None:
            y_df, X_df = create_design_matrices(self.formula, self.data)
            self.y = y_df.values.ravel()
            self.X = X_df.values
            self.var_names = list(X_df.columns)
            self.dependent_var = y_df.columns[0]
        elif self.y is not None and self.X is not None:
            if self.var_names is None:
                self.var_names = [f'x{i}' for i in range(self.X.shape[1])]
            self.dependent_var = 'y'
        else:
            raise ValueError("Must provide either (formula, data) or (y, X)")
        
        # Handle clustering
        cluster_var = None
        if cluster and self.data is not None:
            cluster_var = self.data[cluster]
        
        # Estimate model
        results = self.estimator.estimate(
            self.y, self.X, robust=robust, cluster=cluster_var, **kwargs
        )
        
        # Create results object
        params = pd.Series(results['params'], index=self.var_names)
        std_errors = pd.Series(results['std_errors'], index=self.var_names)
        
        model_info = {
            'model_type': 'OLS',
            'method': 'Least Squares',
            'robust': robust,
            'cluster': cluster
        }
        
        data_info = {
            'nobs': results['nobs'],
            'df_model': results['df_model'],
            'df_resid': results['df_resid'],
            'dependent_var': self.dependent_var,
            'fitted_values': results['fitted_values'],
            'residuals': results['residuals']
        }
        
        diagnostics = {
            'R-squared': results['r_squared'],
            'Adj. R-squared': results['adj_r_squared'],
            'F-statistic': results['f_statistic'],
            'Prob (F-statistic)': results['f_pvalue'],
            'Log-Likelihood': np.nan,  # TODO: implement
            'AIC': np.nan,  # TODO: implement
            'BIC': np.nan   # TODO: implement
        }
        
        self._results = EconometricResults(
            params=params,
            std_errors=std_errors,
            model_info=model_info,
            data_info=data_info,
            diagnostics=diagnostics
        )
        
        self.is_fitted = True
        return self._results
    
    def predict(self, data: Optional[pd.DataFrame] = None) -> np.ndarray:
        """
        Generate predictions
        
        Parameters
        ----------
        data : pd.DataFrame, optional
            Data for prediction
            
        Returns
        -------
        np.ndarray
            Predicted values
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        if data is None:
            return self._results.fitted_values()
        
        # TODO: Implement out-of-sample prediction
        raise NotImplementedError("Out-of-sample prediction not yet implemented")


def regress(
    formula: str,
    data: pd.DataFrame,
    robust: str = 'nonrobust',
    cluster: Optional[str] = None,
    **kwargs
) -> EconometricResults:
    """
    Convenient function for OLS regression
    
    Parameters
    ----------
    formula : str
        Regression formula
    data : pd.DataFrame
        Data containing variables
    robust : str, default 'nonrobust'
        Type of standard errors
    cluster : str, optional
        Variable name for clustering
    **kwargs
        Additional options
        
    Returns
    -------
    EconometricResults
        Fitted model results
        
    Examples
    --------
    >>> results = regress("wage ~ education + experience", data=df)
    >>> print(results.summary())
    
    >>> results = regress("wage ~ education + experience", data=df, 
    ...                   robust='hc1', cluster='firm_id')
    """
    model = OLSRegression(formula=formula, data=data)
    return model.fit(robust=robust, cluster=cluster, **kwargs)
