import Image from 'next/image'
import { Inter } from 'next/font/google'
import Link from 'next/link'
import { useRouter } from 'next/router';
import { useState } from 'react';
import dualBall from '../assets/gif/dual_ball.gif';

const inter = Inter({ subsets: ['latin'] })

export default function Home() {


  const router = useRouter();
  const [loading, setLoading] = useState(false);

  // Function to handle link click
  const handleClick = async (e) => {
    e.preventDefault(); // Prevent default link behavior
    setLoading(true); // Set loading state to true
    const href = e.currentTarget.getAttribute('href');
    await router.push(href); // Navigate to the new page
    setLoading(false); // Set loading state back to false after navigation is complete
  };

  return (
    <main className="flex justify-center items-center h-screen bg-gray-800">
      <div className="text-center">
        <p className="text-4xl font-bold">
          <span className="text-pink-500">security</span>
          <span className="text-white">cell</span>
        </p>
      </div>
    </main>
  )
}
