(() => {
  const header = document.querySelector('[data-header]');
  const navToggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.site-nav');
  let lastScroll = window.scrollY;

  if (navToggle && nav) {
    navToggle.addEventListener('click', () => {
      const open = navToggle.getAttribute('aria-expanded') === 'true';
      navToggle.setAttribute('aria-expanded', String(!open));
      nav.classList.toggle('is-open', !open);
    });
    nav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
      navToggle.setAttribute('aria-expanded', 'false');
      nav.classList.remove('is-open');
    }));
  }

  window.addEventListener('scroll', () => {
    const current = window.scrollY;
    if (header && current > 180 && current > lastScroll + 8) header.classList.add('is-hidden');
    else if (header && current < lastScroll - 8) header.classList.remove('is-hidden');
    lastScroll = current;
  }, { passive: true });

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const revealNodes = [...document.querySelectorAll('.reveal')];
  if (reducedMotion.matches || !('IntersectionObserver' in window)) {
    revealNodes.forEach(node => node.classList.add('is-visible'));
  } else {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: .12 });
    revealNodes.forEach(node => observer.observe(node));
  }

  const tiltScene = document.querySelector('[data-tilt-scene]');
  if (tiltScene && !reducedMotion.matches && window.matchMedia('(pointer:fine)').matches) {
    tiltScene.addEventListener('pointermove', event => {
      const rect = tiltScene.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - .5;
      const y = (event.clientY - rect.top) / rect.height - .5;
      tiltScene.style.setProperty('--ry', `${x * 7}deg`);
      tiltScene.style.setProperty('--rx', `${y * -5}deg`);
    });
    tiltScene.addEventListener('pointerleave', () => {
      tiltScene.style.setProperty('--ry', '0deg');
      tiltScene.style.setProperty('--rx', '0deg');
    });
  }

  const scenarios = {
    transactions: {
      dataset: 'Merchant Transaction Events', code: 'DUC-001 · TERMS V1.0', owner: 'Merchant Data Product', freshness: 'Event-time monitored', quality: 'Priority fields rated', service: 'Under-24h target', status: 'APPROVED', statusKey: 'approved', title: 'Use with explicit boundaries.', copy: 'Transaction events can support bounded anomaly detection and merchant reporting when authoritative fields, latency expectations, and escalation ownership are explicit.', use: 'Anomaly detection and merchant reporting', authority: 'Fraud, finance, and merchant owners retain final decisions', restriction: 'No autonomous financial adjustment', evidence: 'Completeness, duplicates, latency, dispute rate'
    },
    fulfillment: {
      dataset: 'Gift Fulfillment Telemetry', code: 'DUC-014 · TERMS V0.8', owner: 'Fulfillment Operations', freshness: 'Near-real-time target', quality: 'Critical events rated', service: 'Seasonal escalation path', status: 'CONDITIONAL', statusKey: 'conditional', title: 'Use after lineage is complete.', copy: 'Fulfillment telemetry can support delay prediction and exception prioritization, but machine, order, and carrier events must reconcile before the output drives customer promises.', use: 'Delay prediction and exception prioritization', authority: 'Operations retains intervention and promise authority', restriction: 'No customer promise without reconciled order state', evidence: 'Event gaps, sequence integrity, prediction error, intervention outcome'
    },
    support: {
      dataset: 'Customer Support Knowledge', code: 'DUC-027 · TERMS V1.3', owner: 'Customer Experience', freshness: 'Change-event reviewed', quality: 'Authority coverage tracked', service: 'Owner review required', status: 'APPROVED', statusKey: 'approved', title: 'Answer with authority attached.', copy: 'Support knowledge can ground employee and customer-facing assistants when source authority, effective dates, entitlement boundaries, and escalation behavior travel with the answer.', use: 'Grounded support answers and agent assist', authority: 'Support leaders own policy and exception decisions', restriction: 'Abstain when source authority or entitlement is incomplete', evidence: 'Grounding, abstention, escalation, first-contact resolution'
    },
    catalog: {
      dataset: 'Partner Product Catalog', code: 'DUC-033 · TERMS V0.5', owner: 'Partner Integrations', freshness: 'Partner-feed dependent', quality: 'Coverage gaps visible', service: 'Remediation owner pending', status: 'HOLD', statusKey: 'hold', title: 'Do not hide an unowned gap.', copy: 'Catalog data should remain on hold for AI recommendations when ownership, refresh behavior, or merchant eligibility rules are incomplete. The card makes the blocker explicit instead of letting ambiguity travel downstream.', use: 'Discovery only after ownership and eligibility controls pass', authority: 'Partnerships and merchant operations define eligible offers', restriction: 'No recommendation or issuance from unresolved records', evidence: 'Coverage, staleness, eligibility conflicts, partner response time'
    }
  };

  const studio = document.getElementById('issuance-studio');
  if (!studio) return;

  const byId = id => document.getElementById(id);
  const nodes = {
    dataset: byId('card-dataset'), code: byId('card-code'), owner: byId('card-owner'), freshness: byId('card-freshness'), quality: byId('card-quality'), service: byId('card-service'), cardStatus: byId('card-status-label'), machineStatus: byId('machine-status'), machineSequence: byId('machine-sequence'), posture: byId('posture-label'), title: byId('posture-title'), copy: byId('posture-copy'), use: byId('approved-use'), authority: byId('human-authority'), restriction: byId('restriction'), evidence: byId('evidence'), announcement: byId('scenario-announcement')
  };

  let activeKey = 'transactions';
  let animationTimer = null;
  let sequenceNumber = 0;

  const stateColors = { approved: '#ff8900', conditional: '#c98326', hold: '#b85d53' };

  function applyScenario(key, animate = true) {
    const scenario = scenarios[key];
    if (!scenario) return;
    activeKey = key;
    sequenceNumber += 1;
    const thisSequence = sequenceNumber;
    if (animationTimer) window.clearTimeout(animationTimer);

    document.querySelectorAll('.scenario-button').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.scenario === key));
    });

    Object.assign(studio.dataset, { status: scenario.statusKey });
    nodes.dataset.textContent = scenario.dataset;
    nodes.code.textContent = scenario.code;
    nodes.owner.textContent = scenario.owner;
    nodes.freshness.textContent = scenario.freshness;
    nodes.quality.textContent = scenario.quality;
    nodes.service.textContent = scenario.service;
    nodes.cardStatus.textContent = scenario.status;
    nodes.machineStatus.textContent = scenario.status;
    nodes.machineSequence.textContent = `ISSUING ${scenario.code.split(' · ')[0]}`;
    nodes.posture.textContent = scenario.status;
    nodes.posture.style.backgroundColor = stateColors[scenario.statusKey];
    nodes.title.textContent = scenario.title;
    nodes.copy.textContent = scenario.copy;
    nodes.use.textContent = scenario.use;
    nodes.authority.textContent = scenario.authority;
    nodes.restriction.textContent = scenario.restriction;
    nodes.evidence.textContent = scenario.evidence;
    nodes.announcement.textContent = `${scenario.dataset}. ${scenario.status}. ${scenario.title}`;

    studio.classList.remove('is-processing');
    void studio.offsetWidth;
    if (animate && !reducedMotion.matches) {
      studio.classList.add('is-processing');
      animationTimer = window.setTimeout(() => {
        if (sequenceNumber === thisSequence) studio.classList.remove('is-processing');
      }, 1120);
    }
  }

  document.querySelectorAll('.scenario-button').forEach(button => {
    button.addEventListener('click', () => applyScenario(button.dataset.scenario));
  });

  const replay = byId('replay-card');
  const reset = byId('reset-card');
  if (replay) replay.addEventListener('click', () => applyScenario(activeKey));
  if (reset) reset.addEventListener('click', () => applyScenario('transactions'));

  applyScenario('transactions', false);
})();
