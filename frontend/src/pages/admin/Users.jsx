import React from 'react';

/**
 * User/role/organization management (creating users, assigning SANAD
 * groups, managing medical cabinets/labs/pharmacies) is intentionally
 * NOT reimplemented as a separate React CRUD here. Odoo's native
 * Settings > Users interface already does this correctly, safely, and
 * with full validation against res.users/res.groups - building a
 * parallel, partial reimplementation in React would either be a fake
 * surface or a real but redundant duplication of Odoo's own admin UI.
 * This page links directly to the real backend instead.
 */
export default function AdminUsers() {
  const odooBase = import.meta.env.VITE_ODOO_URL || '';
  return (
    <div className="sanad-page">
      <h1>Users & Roles</h1>
      <div className="sanad-card">
        <p>
          User creation, SANAD role assignment (Admin / Doctor / Patient / Laboratory / Pharmacy),
          and organization management (medical cabinets, laboratories, pharmacies) are managed
          through the Odoo backend administration interface.
        </p>
        <a
          className="sanad-btn sanad-btn-primary"
          href={`${odooBase}/odoo/settings/users`}
          target="_blank"
          rel="noreferrer"
        >
          Open Odoo Settings → Users
        </a>
        <a
          className="sanad-btn sanad-btn-secondary"
          href={`${odooBase}/odoo/sanad`}
          target="_blank"
          rel="noreferrer"
        >
          Open SANAD Backend App
        </a>
      </div>
    </div>
  );
}
