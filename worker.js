addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

const users = {
  user1: {
    rotating: false,
    statuses: ["1", "2"],
    custom_status: "rre",
    dnd_enabled: true,
    dnd_message: "",
    dnd_start: "22:00",
    dnd_end: "06:00",
    indicator: "idle",
    rotation_interval_seconds: 60  // Rotate every 30 seconds
  }
}

async function handleRequest(request) {
  const url = new URL(request.url)
  const username = url.pathname.slice(1) // remove leading slash

  if (!users[username]) {
    return new Response(JSON.stringify({ error: "User not found" }), {
      status: 404,
      headers: { 'Content-Type': 'application/json' }
    })
  }

  return new Response(JSON.stringify(users[username]), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  })
}
