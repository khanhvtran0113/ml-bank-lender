import React, { useState } from "react";
import { clearMessages, sendMessage } from "../util/backend";
import ReactMarkdown from "react-markdown";

interface Message {
  id: number;
  text: string;
  sender: "user" | "bot";
}

export const ChatDialog = React.memo(
  ({ lendeeName }: { lendeeName: string }) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputText, setInputText] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const handleSendMessage = React.useCallback(async () => {
      if (isLoading) {
        return;
      }

      if (inputText.trim()) {
        const newMessage: Message = {
          id: messages.length + 1,
          text: inputText,
          sender: "user",
        };
        setMessages((prevMessages) => [...prevMessages, newMessage]);

        setIsLoading(true);
        setInputText("Loading...");
        const response: any = await sendMessage(lendeeName, newMessage.text);

        // Simulate bot response
        const botResponse: Message = {
          id: messages.length + 2,
          text: response,
          sender: "bot",
        };
        setMessages((prevMessages) => [...prevMessages, botResponse]);
        setInputText("");
        setIsLoading(false);
      }
    }, [inputText, lendeeName, messages.length, isLoading]);

    const handleClear = React.useCallback(async () => {
      if (isLoading) {
        return;
      }

      setIsLoading(true);
      setInputText("Loading...");
      await clearMessages(lendeeName);
      setMessages([]);
      setInputText("");
      setIsLoading(false);
    }, [isLoading, lendeeName, setIsLoading, setMessages]);

    return (
      <div className="flex flex-col w-full mx-auto p-4 bg-white rounded-lg border border-gray-300 shadow-lg">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`p-3 rounded-lg max-w-xs break-words ${
                  message.sender === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 text-black"
                }`}
              >
                <ReactMarkdown>{message.text}</ReactMarkdown>
              </div>
            </div>
          ))}
        </div>
        <div className="flex items-center space-x-2 mt-4">
          <input
            type="text"
            className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Ask me anything about the bank statement..."
            disabled={isLoading}
          />
          <button
            className="p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none"
            onClick={handleSendMessage}
            disabled={isLoading}
          >
            Send
          </button>
          <button
            className="p-2 bg-gray-500 text-white rounded-lg hover:bg-gray-700 focus:outline-none"
            onClick={handleClear}
            disabled={isLoading}
          >
            Clear
          </button>
        </div>
      </div>
    );
  }
);
