# MediLink_insurance_utils.py
# Insurance type enhancement utilities extracted from enhanced implementations
# Provides safe helper functions for production integration
# Python 3.4.4 compatible implementation

import time
import json

try:
    from MediLink import MediLink_ConfigLoader
    from MediLink import MediLink_UI
except ImportError:
    import MediLink_ConfigLoader
    import MediLink_UI

# Feature flag system
def get_feature_flag(flag_name, default=False):
    """Centralized feature flag management"""
    try:
        config, _ = MediLink_ConfigLoader.load_configuration()
        feature_flags = config.get("MediLink_Config", {}).get("feature_flags", {})
        return feature_flags.get(flag_name, default)
    except Exception as e:
        MediLink_ConfigLoader.log("Error reading feature flag {}: {}".format(flag_name, str(e)), level="WARNING")
        return default

# Enhanced insurance type validation
def validate_insurance_type_from_config(insurance_type_code, payer_id=""):
    """
    Validate insurance type against configuration with proper logging.
    Returns validated type or safe fallback.
    """
    try:
        config, _ = MediLink_ConfigLoader.load_configuration()
        insurance_options = config['MediLink_Config'].get('insurance_options', {})
        
        if not insurance_type_code:
            MediLink_ConfigLoader.log("Empty insurance type code for payer {}, using default PPO".format(payer_id), level="WARNING")
            return '12'  # Default to PPO
        
        # Direct lookup - insurance type already in config
        if insurance_type_code in insurance_options:
            MediLink_ConfigLoader.log("Validated insurance type '{}' for payer {}".format(
                insurance_type_code, payer_id), level="DEBUG")
            return insurance_type_code
        
        # Unknown type - log and fallback
        MediLink_ConfigLoader.log("UNKNOWN insurance type '{}' for payer {} - using PPO fallback".format(
            insurance_type_code, payer_id), level="WARNING")
        
        return '12'  # Safe fallback to PPO
        
    except Exception as e:
        MediLink_ConfigLoader.log("Insurance validation error: {} - using PPO fallback".format(str(e)), level="ERROR")
        return '12'

# Enhanced patient data enrichment
def enrich_patient_data_with_metadata(detailed_patient_data, insurance_source='MANUAL'):
    """
    Add metadata to patient data for tracking and monitoring.
    Safe enhancement that doesn't break existing functionality.
    """
    enhanced_data = []
    
    for data in detailed_patient_data:
        # Create enhanced copy
        enhanced_record = data.copy()
        
        # Add metadata fields
        enhanced_record['insurance_type_source'] = insurance_source
        enhanced_record['insurance_type_validated'] = True
        enhanced_record['insurance_type_timestamp'] = time.time()
        enhanced_record['insurance_type_metadata'] = {}
        
        enhanced_data.append(enhanced_record)
    
    return enhanced_data

# Insurance type assignment logging
def log_insurance_type_decision(patient_id, insurance_type, source, metadata=None):
    """Enhanced logging for insurance type assignments"""
    log_data = {
        'patient_id': patient_id,
        'insurance_type': insurance_type,
        'source': source,
        'timestamp': time.time()
    }
    if metadata:
        log_data['metadata'] = metadata
    
    MediLink_ConfigLoader.log("Insurance assignment: {}".format(json.dumps(log_data)), level="INFO")

# Monitoring and statistics
def generate_insurance_assignment_summary(detailed_patient_data):
    """
    Generate summary statistics for insurance type assignments.
    Helps monitor system performance and data quality.
    """
    if not detailed_patient_data:
        return {}
    
    # Collect statistics
    source_counts = {}
    insurance_type_counts = {}
    
    for data in detailed_patient_data:
        source = data.get('insurance_type_source', 'UNKNOWN')
        insurance_type = data.get('insurance_type', 'UNKNOWN')
        
        source_counts[source] = source_counts.get(source, 0) + 1
        insurance_type_counts[insurance_type] = insurance_type_counts.get(insurance_type, 0) + 1
    
    total_patients = len(detailed_patient_data)
    
    summary = {
        'total_patients': total_patients,
        'sources': source_counts,
        'insurance_types': insurance_type_counts,
        'timestamp': time.time()
    }
    
    # Log summary
    MediLink_ConfigLoader.log("Insurance Assignment Summary: {}".format(json.dumps(summary)), level="INFO")
    
    return summary

# Safe wrapper for insurance type selection
def safe_insurance_type_selection(parsed_data, fallback_function):
    """
    Safe wrapper that attempts enhanced selection with fallback to original function.
    Provides comprehensive error handling and logging.
    """
    patient_name = parsed_data.get('LAST', 'UNKNOWN')
    
    try:
        # Check if enhanced mode is enabled
        enhanced_mode = get_feature_flag('enhanced_insurance_selection', default=False)
        
        if enhanced_mode:
            # Try enhanced selection (would be implemented here)
            MediLink_ConfigLoader.log("Attempting enhanced insurance selection for {}".format(patient_name), level="DEBUG")
            # For now, just call fallback - actual enhancement would go here
            result = fallback_function(parsed_data)
            log_insurance_type_decision(patient_name, result, 'ENHANCED')
            return result
        else:
            # Use standard selection
            result = fallback_function(parsed_data)
            log_insurance_type_decision(patient_name, result, 'MANUAL')
            return result
            
    except Exception as e:
        # Error handling with safe fallback
        MediLink_ConfigLoader.log("Insurance selection error for {}: {}. Using PPO default.".format(
            patient_name, str(e)), level="ERROR")
        
        log_insurance_type_decision(patient_name, '12', 'ERROR_FALLBACK', {'error': str(e)})
        return '12'  # Safe fallback

# Configuration validation
def validate_insurance_configuration():
    """
    Validate insurance configuration for production readiness.
    Returns True if valid, raises exception if invalid.
    """
    try:
        config, _ = MediLink_ConfigLoader.load_configuration()
        insurance_options = config['MediLink_Config'].get('insurance_options', {})
        
        if not insurance_options:
            raise ValueError("Missing insurance_options in MediLink_Config")
        
        # Validate insurance options format
        for code, description in insurance_options.items():
            if not isinstance(code, str) or len(code) < 1:
                raise ValueError("Invalid insurance code format: {}".format(code))
            if not isinstance(description, str):
                raise ValueError("Invalid insurance description for code: {}".format(code))
        
        MediLink_ConfigLoader.log("Insurance configuration validation passed: {} options loaded".format(
            len(insurance_options)), level="INFO")
        return True
        
    except Exception as e:
        MediLink_ConfigLoader.log("Insurance configuration validation failed: {}".format(str(e)), level="ERROR")
        raise e

# Production readiness check
def check_production_readiness():
    """
    Check if system is ready for production deployment.
    Returns list of warnings/errors that need attention.
    """
    issues = []
    
    try:
        # Check configuration
        validate_insurance_configuration()
    except Exception as e:
        issues.append("Configuration invalid: {}".format(str(e)))
    
    # Check for test mode flags
    try:
        config, _ = MediLink_ConfigLoader.load_configuration()
        test_mode = config.get("MediLink_Config", {}).get("TestMode", False)
        if test_mode:
            issues.append("TestMode is enabled - should be disabled for production")
    except Exception as e:
        issues.append("Cannot check test mode: {}".format(str(e)))
    
    return issues

# Enhanced error handling wrapper
def with_insurance_error_handling(func):
    """
    Decorator for insurance-related functions to add consistent error handling.
    Python 3.4.4 compatible implementation.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            MediLink_ConfigLoader.log("Insurance function error in {}: {}".format(func.__name__, str(e)), level="ERROR")
            # Return safe defaults based on function type
            if 'insurance_type' in func.__name__:
                return '12'  # Default PPO for insurance type functions
            else:
                raise e  # Re-raise for non-insurance type functions
    return wrapper

# Utility for batch processing with progress tracking
def process_patients_with_progress(patients, processing_function, description="Processing patients"):
    """
    Process patients with progress tracking and error collection.
    Returns processed results and error summary.
    """
    processed_results = []
    errors = []
    
    try:
        from tqdm import tqdm
        iterator = tqdm(patients, desc=description)
    except ImportError:
        iterator = patients
        MediLink_ConfigLoader.log("Processing {} patients (tqdm not available)".format(len(patients)), level="INFO")
    
    for i, patient in enumerate(iterator):
        try:
            result = processing_function(patient)
            processed_results.append(result)
        except Exception as e:
            error_info = {
                'patient_index': i,
                'patient_id': patient.get('patient_id', 'UNKNOWN'),
                'error': str(e)
            }
            errors.append(error_info)
            MediLink_ConfigLoader.log("Error processing patient {}: {}".format(
                patient.get('patient_id', i), str(e)), level="ERROR")
    
    if errors:
        MediLink_ConfigLoader.log("Batch processing completed with {} errors out of {} patients".format(
            len(errors), len(patients)), level="WARNING")
    
    return processed_results, errors