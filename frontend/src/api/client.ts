const API_URL = import.meta.env.VITE_API_URL || '';

export async function apiRequest(path: string, options: RequestInit = {}) {
    const url = `${API_URL}${path}`;

    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options.headers,
        },
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API error ${response.status}`);
    }

    return response.json();
}
