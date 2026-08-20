import Link from 'next/link';

export default function HomePage() {
  return (
    <main style={{ padding: '2rem' }}>
      <h1>Aircraft Predictive Maintenance</h1>
      <p>Supervisor dashboard overview.</p>
      <nav style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
        <Link href='/dashboard'>Dashboard</Link>
        <Link href='/engines/engine-001'>Engine Details</Link>
        <Link href='/alerts'>Alerts</Link>
      </nav>
    </main>
  );
}
