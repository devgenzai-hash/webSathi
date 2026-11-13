import { Link } from 'react-router-dom';
import { Check } from 'lucide-react';

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: '/month',
    description: 'Get started with AI chatbots',
    features: [
      '2 websites',
      '100 messages/month',
      '5 documents per site',
      'Community models (Ollama, llama.cpp)',
      'Basic support',
    ],
    cta: 'Get Started',
    highlighted: false,
  },
  {
    name: 'Starter',
    price: '$29',
    period: '/month',
    description: 'For growing businesses',
    features: [
      '5 websites',
      '5,000 messages/month',
      '50 documents per site',
      'GPT-4o-mini, DeepSeek, Llama 3.1',
      'Priority support',
      'Custom branding',
    ],
    cta: 'Coming Soon',
    highlighted: true,
  },
  {
    name: 'Pro',
    price: '$99',
    period: '/month',
    description: 'For large scale deployments',
    features: [
      '20 websites',
      'Unlimited messages',
      'Unlimited documents',
      'All models (GPT-4o, Claude, etc.)',
      'Dedicated support',
      'Custom branding',
      'Analytics dashboard',
      'API access',
    ],
    cta: 'Coming Soon',
    highlighted: false,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    description: 'For organizations',
    features: [
      'Unlimited everything',
      'Self-hosted option',
      'Custom model fine-tuning',
      'SSO / SAML',
      'SLA guarantees',
      'Dedicated account manager',
    ],
    cta: 'Contact Us',
    highlighted: false,
  },
];

export default function Pricing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white py-16 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900">Simple, Transparent Pricing</h1>
          <p className="text-gray-500 mt-3 text-lg">Start free, scale as you grow</p>
          <p className="text-sm text-yellow-600 bg-yellow-50 inline-block px-4 py-2 rounded-full mt-4">
            🎉 All plans are FREE during beta! Pricing will be applied later.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`rounded-2xl p-6 ${plan.highlighted ? 'bg-primary-600 text-white ring-4 ring-primary-200 scale-105' : 'bg-white border border-gray-200'}`}
            >
              <h3 className={`text-lg font-bold ${plan.highlighted ? 'text-white' : 'text-gray-900'}`}>{plan.name}</h3>
              <div className="mt-2">
                <span className="text-3xl font-bold">{plan.price}</span>
                <span className={`text-sm ${plan.highlighted ? 'text-primary-200' : 'text-gray-500'}`}>{plan.period}</span>
              </div>
              <p className={`text-sm mt-2 ${plan.highlighted ? 'text-primary-200' : 'text-gray-500'}`}>{plan.description}</p>
              
              <ul className="mt-6 space-y-3">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-2 text-sm">
                    <Check size={16} className={`mt-0.5 flex-shrink-0 ${plan.highlighted ? 'text-primary-200' : 'text-green-500'}`} />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                className={`w-full mt-6 py-2 rounded-lg font-medium transition-colors ${plan.highlighted ? 'bg-white text-primary-700 hover:bg-primary-50' : 'bg-primary-600 text-white hover:bg-primary-700'}`}
                disabled={plan.cta === 'Coming Soon'}
              >
                {plan.cta}
              </button>
            </div>
          ))}
        </div>

        <div className="text-center mt-8">
          <Link to="/login" className="text-primary-600 hover:underline text-sm">← Back to Dashboard</Link>
        </div>
      </div>
    </div>
  );
}
