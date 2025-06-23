const stepsLg = [
  {
    title: '<span class="text-primary">Welcome to Wildlandfireresource</span> 👋',
    intro: 'This quick tour will guide you through the key areas of the platform to help you get started.',
  },
  {
    id: 'step-nav-dash',
    element: '#dash',
    title: '<span class="text-primary">Dashboard Overview</span>',
    intro: 'Access real-time summaries, recent activity, and key insights about your operations.',
    position: 'right',
  },
  {
    id: 'step-nav-agreements',
    element: '#agreements',
    title: '<span class="text-primary">Upload Agreements</span>',
    intro: 'Here you can upload and manage your Agreement Contracts.',
    position: 'right',
  },
  {
    id: 'step-nav-ro',
    element: '#ro',
    title: '<span class="text-primary">Manage Resource Orders</span>',
    intro: 'Easily create, track, and manage Resource Order Forms required.',
    position: 'right',
  },
  {
    id: 'step-nav-st',
    element: '#st',
    title: '<span class="text-primary">Create Shift Tickets</span>',
    intro: 'Generate Shift Tickets for personnel and equipment assigned to incidents.',
    position: 'right',
  },
  {
    id: 'step-nav-eval',
    element: '#ev',
    title: '<span class="text-primary">Submit Evaluations</span>',
    intro: 'Generate and submit Evaluation Forms to track performance and compliance.',
    position: 'right',
  },
  {
    id: 'step-nav-pr',
    element: '#pr',
    title: '<span class="text-primary">Your Profile</span>',
    intro: 'Access your profile to update contact information and credentials.',
    position: 'right',
  },
  {
    id: 'step-nav-pr-alt',
    element: '#pr-alt',
    title: '<span class="text-primary">Alternate Profile Access</span>',
    intro: 'You can also manage your profile from this quick link.',
    position: 'right',
  },
  {
    id: 'step-expand',
    element: '#toggle-sidebar',
    title: '<span class="text-primary">Sidebar Toggle</span>',
    intro: 'Use this button to collapse or expand the sidebar for more workspace.',
    position: 'right',
  }
];


 const stepsSm = [
            {
                title: '<span class="text-primary">Welcome to Wildlandfireresource</span> 👋',
                intro: 'This quick tour will guide you through the key areas of the platform to help you get started.',
            },
            {
                title: '<span class="text-primary">Sidebar Menu</span>',
                intro: 'Use the menu button "☰"(top right) to expand and collapse the sidebar.',
            },
            {
                title: '<span class="text-primary">Dashboard Overview</span>',
                intro: 'Access real-time summaries, recent activity, and key insights about your operations.',            },
            {
                title: '<span class="text-primary">Upload Agreements</span>',
                intro: 'Here you can upload and manage your Agreement Contracts.',
            },
            {
                title: '<span class="text-primary">Manage Resource Orders</span>',
                intro: 'Easily create, track, and manage Resource Order Forms required.',
            },
            {
                title: '<span class="text-primary">Create Shift Tickets</span>',
                intro: 'Generate Shift Tickets for personnel and equipment assigned to incidents.',
            },
            {
                title: '<span class="text-primary">Submit Evaluations</span>',
                intro: 'Generate and submit Evaluation Forms to track performance and compliance.',
            },
            {
                title: '<span class="text-primary">Your Profile</span>',
                intro: 'Access your profile to update contact information and credentials.',
            },
            {
                id: 'step-nav-pr-alt',
                element: '#pr-alt-sm',
                title: '<span class="text-primary">Alternate Profile Access</span>',
                intro: 'You can also manage your profile from this quick link.',
            },
        ]

function startIntroOnce() {
    // Only run if the intro hasn't been shown before
    const localStorageKey = `intro_shown`;

    if (localStorage.getItem(localStorageKey)) return;

    introJs()
        .setOptions({
          steps: window.innerWidth > 820 ? stepsLg: stepsSm,
          buttonClass: 'btn btn-inverse-primary',
        })
        .oncomplete(() => {
            localStorage.setItem(localStorageKey, 'true');
        })
        .onexit(() => {
            localStorage.setItem(localStorageKey, 'true');
        })
        .start()
    ;
}

startIntroOnce()
