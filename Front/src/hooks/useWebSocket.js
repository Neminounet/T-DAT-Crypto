// useWebSocket.js

import { useEffect } from 'react';
import { Client } from '@stomp/stompjs';
import SockJS from 'sockjs-client';

const useWebSocket = (setCryptoData, setError) => {
  useEffect(() => {
    const socket = new SockJS('http://localhost:8080/ws');
    const client = new Client({
      webSocketFactory: () => socket,
      reconnectDelay: 5000,
      debug: (str) => console.log(str),
    });

    client.onConnect = () => {
      console.log('Connecté au WebSocket via STOMP');
      client.subscribe('/topic/price/', (message) => {
        const updates = JSON.parse(message.body);
        console.log('Received WebSocket message:', updates);

        if (Array.isArray(updates)) {
          setCryptoData((prevData) => {
            const updatesMap = updates.reduce((map, update) => {
              map[update.asset] = update;
              return map;
            }, {});

            return prevData.map((crypto) => {
              if (updatesMap[crypto.asset]) {
                return {
                  ...crypto,
                  price: updatesMap[crypto.asset].price,
                  timestamp: updatesMap[crypto.asset].timestamp,
                };
              }
              return crypto;
            });
          });
        } else if (updates && updates.asset && updates.price) {
          setCryptoData((prevData) =>
            prevData.map((crypto) =>
              crypto.asset === updates.asset
                ? { ...crypto, price: updates.price, timestamp: updates.timestamp }
                : crypto
            )
          );
        }
      });
    };

    client.onStompError = (error) => {
      console.error('Erreur STOMP:', error);
      setError('Erreur de connexion STOMP');
    };

    client.activate();

    return () => {
      client.deactivate();
    };
  }, [setCryptoData, setError]);
};

export default useWebSocket;
