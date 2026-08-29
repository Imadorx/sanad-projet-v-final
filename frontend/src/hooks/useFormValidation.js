import { useState, useCallback } from 'react';

/**
 * Minimal client-side form validation hook. Client-side validation is a
 * UX convenience only - every field is still validated/constrained on
 * the backend (required=True, @api.constrains, ir.rule) as the actual
 * source of truth, so this never needs to duplicate business rules,
 * only catch obviously-empty/malformed input before a round trip.
 */
export function useFormValidation(initialValues, validators) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});

  const setField = useCallback((name, value) => {
    setValues((v) => ({ ...v, [name]: value }));
    setErrors((e) => ({ ...e, [name]: undefined }));
  }, []);

  const validate = useCallback(() => {
    const newErrors = {};
    for (const [field, validator] of Object.entries(validators || {})) {
      const message = validator(values[field], values);
      if (message) newErrors[field] = message;
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [values, validators]);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { values, errors, setField, validate, reset, setValues };
}

export const validators = {
  required: (label) => (value) =>
    value === undefined || value === null || value === '' ? `${label} is required.` : undefined,
  minLength: (label, min) => (value) =>
    value && value.length < min ? `${label} must be at least ${min} characters.` : undefined,
};
