from sklearn.base import BaseEstimator, RegressorMixin, ClassifierMixin
from sklearn.ensemble import (
    RandomForestRegressor, RandomForestClassifier,
    GradientBoostingRegressor, GradientBoostingClassifier
)

from automodeling.base import AutoModelBase

import logging

logging.getLogger("optuna").setLevel(logging.WARNING)


class AutoRandomForestRegressor(AutoModelBase, BaseEstimator, RegressorMixin):
    def __init__(
            self,
            n_estimators=100,
            criterion='squared_error',
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1,
            min_weight_fraction_leaf=0.0,
            max_features=1.0,
            max_leaf_nodes=None,
            min_impurity_decrease=0.0,
            bootstrap=True,
            oob_score=False,
            n_jobs=None,
            random_state=None,
            ccp_alpha=0.0,
            max_samples=None,
            auto_scoring=None,
            auto_direction='minimize', 
            auto_timeout=60, 
            auto_n_trials=None, 
            auto_verbose=False,
            auto_use_scaler=False
        ):
        super().__init__(
            auto_scoring,
            auto_direction,
            auto_timeout,
            auto_n_trials,
            auto_verbose,
            auto_use_scaler
        )
        self.n_estimators = n_estimators
        self.criterion = criterion
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.min_weight_fraction_leaf = min_weight_fraction_leaf
        self.max_features = max_features
        self.max_leaf_nodes = max_leaf_nodes
        self.min_impurity_decrease = min_impurity_decrease
        self.bootstrap = bootstrap
        self.oob_score = oob_score
        self.n_jobs = n_jobs
        self.random_state = random_state
        self.ccp_alpha = ccp_alpha
        self.max_samples = max_samples
    
    def _get_model_params(self):
        return {
            'n_estimators': self.n_estimators,
            'criterion': self.criterion,
            'max_depth': self.max_depth,
            'min_samples_split': self.min_samples_split,
            'min_samples_leaf': self.min_samples_leaf,
            'min_weight_fraction_leaf': self.min_weight_fraction_leaf,
            'max_features': self.max_features,
            'max_leaf_nodes': self.max_leaf_nodes,
            'min_impurity_decrease': self.min_impurity_decrease,
            'bootstrap': self.bootstrap,
            'oob_score': self.oob_score,
            'n_jobs': self.n_jobs,
            'random_state': self.random_state,
            'ccp_alpha': self.ccp_alpha,
            'max_samples': self.max_samples
        }
    
    def _build_model(self, params):
        return RandomForestRegressor(**params)

    def _get_search_space(self, trial):
        bootstrap = trial.suggest_categorical('bootstrap', [True, False])

        if bootstrap:
            oob_score = trial.suggest_categorical('oob_score', [False, True])
        else:
            oob_score = False

        params = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
            'criterion': trial.suggest_categorical('criterion', ['squared_error', 'absolute_error', 'friedman_mse']),
            'max_depth': trial.suggest_int('max_depth', 3, 30) if trial.suggest_categorical('use_max_depth', [True, False]) else None,
            'min_samples_split': trial.suggest_float('min_samples_split', 0.001, 0.3),
            'min_samples_leaf': trial.suggest_float('min_samples_leaf', 0.001, 0.1),
            'min_weight_fraction_leaf': trial.suggest_float('min_weight_fraction_leaf', 0.0, 0.1),
            'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', None, 1.0, 0.3, 0.7]),
            'max_leaf_nodes': trial.suggest_int('max_leaf_nodes', 10, 100) if trial.suggest_categorical('use_max_leaf_nodes', [True, False]) else None,
            'min_impurity_decrease': trial.suggest_float('min_impurity_decrease', 0.0, 0.01),
            'bootstrap': bootstrap,
            'oob_score': oob_score,
            'n_jobs': -1,
            'random_state': trial.suggest_categorical('random_state', [42]),
            'ccp_alpha': trial.suggest_float('ccp_alpha', 0.0, 0.01),
            'max_samples': trial.suggest_float('max_samples', 0.3, 1.0) if bootstrap else None,
        }
        
        return params

class AutoGradientBoostingRegressor(AutoModelBase, BaseEstimator, RegressorMixin):
    def __init__(
            self,
            loss='squared_error',
            learning_rate=0.1,
            n_estimators=100,
            subsample=1.0,
            criterion='friedman_mse',
            min_samples_split=2,
            min_samples_leaf=1,
            min_weight_fraction_leaf=0.0,
            max_depth=3,
            min_impurity_decrease=0.0,
            random_state=None,
            max_features=None,
            alpha=0.9,
            max_leaf_nodes=None,
            tol=1e-4,
            ccp_alpha=0.0,
            auto_scoring=None,
            auto_direction='minimize', 
            auto_timeout=60, 
            auto_n_trials=None, 
            auto_verbose=False,
            auto_use_scaler=False
        ):
        super().__init__(
            auto_scoring,
            auto_direction,
            auto_timeout,
            auto_n_trials,
            auto_verbose,
            auto_use_scaler
        )
        self.loss = loss
        self.learning_rate = learning_rate
        self.n_estimators = n_estimators
        self.subsample = subsample
        self.criterion = criterion
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.min_weight_fraction_leaf = min_weight_fraction_leaf
        self.max_depth = max_depth
        self.min_impurity_decrease = min_impurity_decrease
        self.random_state = random_state
        self.max_features = max_features
        self.alpha = alpha
        self.max_leaf_nodes = max_leaf_nodes
        self.tol = tol
        self.ccp_alpha = ccp_alpha
        
    
    def _get_model_params(self):
        return {
            'loss': self.loss,
            'learning_rate': self.learning_rate,
            'n_estimators': self.n_estimators,
            'subsample': self.subsample,
            'criterion': self.criterion,
            'min_samples_split': self.min_samples_split,
            'min_samples_leaf': self.min_samples_leaf,
            'min_weight_fraction_leaf': self.min_weight_fraction_leaf,
            'max_depth': self.max_depth,
            'min_impurity_decrease': self.min_impurity_decrease,
            'random_state': self.random_state,
            'max_features': self.max_features,
            'alpha': self.alpha,
            'max_leaf_nodes': self.max_leaf_nodes,
            'tol': self.tol,
            'ccp_alpha': self.ccp_alpha
        }
    
    def _build_model(self, params):
        return GradientBoostingRegressor(**params)

    def _get_search_space(self, trial):        
        params = {
            'loss': trial.suggest_categorical('loss', ['squared_error', 'absolute_error', 'huber', 'quantile']),
            'learning_rate': trial.suggest_float('learning_rate', 0.001, 0.3, log=True),
            'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
            'subsample': trial.suggest_float('subsample', 0.5, 1.0),
            'criterion': trial.suggest_categorical('criterion', ['friedman_mse', 'squared_error']),
            'min_samples_split': trial.suggest_float('min_samples_split', 0.001, 0.3),
            'min_samples_leaf': trial.suggest_float('min_samples_leaf', 0.001, 0.1),
            'min_weight_fraction_leaf': trial.suggest_float('min_weight_fraction_leaf', 0.0, 0.1),
            'max_depth': trial.suggest_int('max_depth', 3, 30),
            'min_impurity_decrease': trial.suggest_float('min_impurity_decrease', 0.0, 0.01),
            'random_state': trial.suggest_categorical('random_state', [42]),
            'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', None, 0.3, 0.7, 1.0]),
            'alpha': trial.suggest_float('alpha', 0.7, 0.99),
            # if trial.suggest_categorical('loss', ['huber', 'quantile', 'squared_error', 'absolute_error']) in ['huber', 'quantile'] else 0.9,
            'max_leaf_nodes': trial.suggest_int('max_leaf_nodes', 10, 100) if trial.suggest_categorical('use_max_leaf_nodes', [True, False]) else None,
            'tol': trial.suggest_float('tol', 1e-6, 1e-2, log=True),
            'ccp_alpha': trial.suggest_float('ccp_alpha', 0.0, 0.01)
        }
        
        return params

class AutoRandomForestClassifier(AutoModelBase, BaseEstimator, ClassifierMixin):
    def __init__(
            self,
            n_estimators=100,
            criterion='gini',
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1,
            min_weight_fraction_leaf=0.0,
            max_features='sqrt',
            max_leaf_nodes=None,
            min_impurity_decrease=0.0,
            bootstrap=True,
            oob_score=False,
            n_jobs=None,
            random_state=None,
            verbose=0,
            warm_start=False,
            class_weight=None,
            ccp_alpha=0.0,
            max_samples=None,
            auto_scoring=None,
            auto_direction='minimize', 
            auto_timeout=60, 
            auto_n_trials=None, 
            auto_verbose=False,
            auto_use_scaler=False
        ):
        super().__init__(
            auto_scoring,
            auto_direction,
            auto_timeout,
            auto_n_trials,
            auto_verbose,
            auto_use_scaler
        )
        self.n_estimators = n_estimators
        self.criterion = criterion
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.min_weight_fraction_leaf = min_weight_fraction_leaf
        self.max_features = max_features
        self.max_leaf_nodes = max_leaf_nodes
        self.min_impurity_decrease = min_impurity_decrease
        self.bootstrap = bootstrap
        self.oob_score = oob_score
        self.n_jobs = n_jobs
        self.random_state = random_state
        self.verbose = verbose
        self.warm_start = warm_start
        self.class_weight = class_weight
        self.ccp_alpha = ccp_alpha
        self.max_samples = max_samples
    
    def _get_model_params(self):
        return {
            'n_estimators': self.n_estimators,
            'criterion': self.criterion,
            'max_depth': self.max_depth,
            'min_samples_split': self.min_samples_split,
            'min_samples_leaf': self.min_samples_leaf,
            'min_weight_fraction_leaf': self.min_weight_fraction_leaf,
            'max_features': self.max_features,
            'max_leaf_nodes': self.max_leaf_nodes,
            'min_impurity_decrease': self.min_impurity_decrease,
            'bootstrap': self.bootstrap,
            'oob_score': self.oob_score,
            'n_jobs': self.n_jobs,
            'random_state': self.random_state,
            'verbose': self.verbose,
            'warm_start': self.warm_start,
            'class_weight': self.class_weight,
            'ccp_alpha': self.ccp_alpha,
            'max_samples': self.max_samples
        }
    
    def _build_model(self, params):
        return RandomForestClassifier(**params)

    def _get_search_space(self, trial):
        bootstrap = trial.suggest_categorical('bootstrap', [True, False])

        if bootstrap:
            oob_score = trial.suggest_categorical('oob_score', [False, True])
        else:
            oob_score = False

        params = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
            'criterion': trial.suggest_categorical('criterion', ['gini', 'entropy', 'log_loss']),
            'max_depth': trial.suggest_int('max_depth', 3, 30) if trial.suggest_categorical('use_max_depth', [True, False]) else None,
            'min_samples_split': trial.suggest_float('min_samples_split', 0.001, 0.3),
            'min_samples_leaf': trial.suggest_float('min_samples_leaf', 0.001, 0.1),
            'min_weight_fraction_leaf': trial.suggest_float('min_weight_fraction_leaf', 0.0, 0.1),
            'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', None, 0.3, 0.7, 1.0]),
            'max_leaf_nodes': trial.suggest_int('max_leaf_nodes', 10, 100) if trial.suggest_categorical('use_max_leaf_nodes', [True, False]) else None,
            'min_impurity_decrease': trial.suggest_float('min_impurity_decrease', 0.0, 0.01),
            'bootstrap': bootstrap,
            'oob_score': oob_score,
            'n_jobs': self.n_jobs,
            'random_state': trial.suggest_categorical('random_state', [42]),
            'verbose': self.verbose,
            'warm_start': self.warm_start,
            'class_weight': trial.suggest_categorical('class_weight', ['balanced', 'balanced_subsample', None]),
            'ccp_alpha': trial.suggest_float('ccp_alpha', 0.0, 0.01),
            'max_samples': trial.suggest_float('max_samples', 0.3, 1.0) if bootstrap else None,
        }
        
        return params
    
class AutoGradientBoostingClassifier(AutoModelBase, BaseEstimator, ClassifierMixin):
    def __init__(
            self,
            loss='log_loss',
            learning_rate=0.1,
            n_estimators=100,
            subsample=1.0,
            criterion='friedman_mse',
            min_samples_split=2,
            min_samples_leaf=1,
            min_weight_fraction_leaf=0.0,
            max_depth=3,
            min_impurity_decrease=0.0,
            init=None,
            random_state=None,
            max_features=None,
            verbose=0,
            max_leaf_nodes=None,
            warm_start=False,
            validation_fraction=0.1,
            n_iter_no_change=None,
            tol=1e-4,
            ccp_alpha=0.0,
            auto_scoring=None,
            auto_direction='minimize', 
            auto_timeout=60, 
            auto_n_trials=None, 
            auto_verbose=False,
            auto_use_scaler=False
        ):
        super().__init__(
            auto_scoring,
            auto_direction,
            auto_timeout,
            auto_n_trials,
            auto_verbose,
            auto_use_scaler
        )
        self.loss = loss
        self.learning_rate = learning_rate
        self.n_estimators = n_estimators
        self.subsample = subsample
        self.criterion = criterion
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.min_weight_fraction_leaf = min_weight_fraction_leaf
        self.max_depth = max_depth
        self.min_impurity_decrease = min_impurity_decrease
        self.init = init
        self.random_state = random_state
        self.max_features = max_features
        self.verbose = verbose
        self.max_leaf_nodes = max_leaf_nodes
        self.warm_start = warm_start
        self.validation_fraction = validation_fraction
        self.n_iter_no_change = n_iter_no_change
        self.tol = tol
        self.ccp_alpha = ccp_alpha
        
    
    def _get_model_params(self):
        return {
            'loss': self.loss,
            'learning_rate': self.learning_rate,
            'n_estimators': self.n_estimators,
            'subsample': self.subsample,
            'criterion': self.criterion,
            'min_samples_split': self.min_samples_split,
            'min_samples_leaf': self.min_samples_leaf,
            'min_weight_fraction_leaf': self.min_weight_fraction_leaf,
            'max_depth': self.max_depth,
            'min_impurity_decrease': self.min_impurity_decrease,
            'init': self.init,
            'random_state': self.random_state,
            'max_features': self.max_features,
            'verbose': self.verbose,
            'max_leaf_nodes': self.max_leaf_nodes,
            'warm_start': self.warm_start,
            'validation_fraction': self.validation_fraction,
            'n_iter_no_change': self.n_iter_no_change,
            'tol': self.tol,
            'ccp_alpha': self.ccp_alpha
        }
    
    def _build_model(self, params):
        return GradientBoostingClassifier(**params)

    def _get_search_space(self, trial):
        params = {
            'loss': trial.suggest_categorical('loss', ['log_loss', 'exponential']),
            'learning_rate': trial.suggest_float('learning_rate', 0.001, 0.3, log=True),
            'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
            'subsample': trial.suggest_float('subsample', 0.5, 1.0),
            'criterion': trial.suggest_categorical('criterion', ['friedman_mse', 'squared_error']),
            'min_samples_split': trial.suggest_float('min_samples_split', 0.001, 0.3) if trial.suggest_categorical('use_min_samples_split', [True, False]) else 2,
            'min_samples_leaf': trial.suggest_float('min_samples_leaf', 0.001, 0.1) if trial.suggest_categorical('use_min_samples_leaf', [True, False]) else 1,
            'min_weight_fraction_leaf': trial.suggest_float('min_weight_fraction_leaf', 0.0, 0.1),
            'max_depth': trial.suggest_int('max_depth', 3, 30),
            'min_impurity_decrease': trial.suggest_float('min_impurity_decrease', 0.0, 0.01),
            'init': self.init,
            'random_state': trial.suggest_categorical('random_state', [42]),
            'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', None, 0.3, 0.7, 1.0]),
            'verbose': self.verbose,
            'max_leaf_nodes': trial.suggest_int('max_leaf_nodes', 10, 100) if trial.suggest_categorical('use_max_leaf_nodes', [True, False]) else None,
            'warm_start': self.warm_start,
            'validation_fraction': trial.suggest_float('validation_fraction', 0.1, 0.3),
            'n_iter_no_change': trial.suggest_int('n_iter_no_change', 1, 10) if trial.suggest_categorical('use_n_iter_no_change', [True, False]) else None,
            'tol': trial.suggest_float('tol', 1e-6, 1e-2, log=True),
            'ccp_alpha': trial.suggest_float('ccp_alpha', 0.0, 0.01)
        }
        
        return params