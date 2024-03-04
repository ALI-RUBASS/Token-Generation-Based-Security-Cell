// pages/MarketPage.tsx

import React from 'react';
import { GetServerSideProps } from 'next';
import Head from 'next/head';

interface MarketData {
  // Define the structure of the data received from the API
  // Adjust these properties according to the actual data structure
  id: number;
  name: string;
  price: number;
}

interface MarketPageProps {
  marketData: MarketData[];
}

const MarketPage: React.FC<MarketPageProps> = ({ marketData }) => {
  return (
    <div>
      <Head>
        <title>Market Page</title>
        <meta name="description" content="Market Page" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        <h1>Market Data</h1>
        <table className="table-auto">
          <thead>
            <tr>
              <th className="px-4 py-2">ID</th>
              <th className="px-4 py-2">Name</th>
              <th className="px-4 py-2">Price</th>
            </tr>
          </thead>
          <tbody>
            {marketData.map((item) => (
              <tr key={item.id}>
                <td className="border px-4 py-2">{item.id}</td>
                <td className="border px-4 py-2">{item.name}</td>
                <td className="border px-4 py-2">{item.price}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </main>
    </div>
  );
};

export const getServerSideProps: GetServerSideProps<MarketPageProps> = async () => {
  // Fetch data from the external API
  const response = await fetch('http://www.gigadevden.com/market.php');
  const data: MarketData[] | undefined = await response.json();

  if (!data) {
    return {
      notFound: true,
    };
  }

  // Pass data to the page component as props
  return {
    props: {
      marketData: data,
    },
  };
};

export default MarketPage;
