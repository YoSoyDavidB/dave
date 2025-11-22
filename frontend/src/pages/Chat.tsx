export default function Chat() {
  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-3xl mx-auto">
          <div className="text-center py-12">
            <h1 className="text-2xl font-bold text-gray-800 mb-2">
              Hey! I'm Dave 👋
            </h1>
            <p className="text-gray-600">
              Your AI friend for productivity and English learning.
              <br />
              Start chatting to organize your life!
            </p>
          </div>
        </div>
      </div>

      {/* Message input */}
      <div className="border-t bg-white p-4">
        <div className="max-w-3xl mx-auto">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Type a message..."
              className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
