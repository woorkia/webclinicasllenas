export default async function handler(req, res) {
  // Solo POST
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { nombre, clinica, email, telefono, tipo, mensaje } = req.body || {};

  // Validación básica
  if (!nombre || !email) {
    return res.status(400).json({ error: 'Nombre y email son obligatorios' });
  }

  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    return res.status(500).json({ error: 'API key no configurada' });
  }

  // HTML del email que llega al equipo de Clínicas Llenas
  const htmlEquipo = `
  <div style="font-family:Inter,sans-serif;max-width:580px;margin:0 auto;background:#fff;border-radius:16px;overflow:hidden;border:1px solid #e2e8f0">
    <div style="background:linear-gradient(135deg,#0D1B2A,#1E3A5F);padding:32px 32px 24px">
      <p style="margin:0 0 4px;font-size:12px;color:#94A3B8;text-transform:uppercase;letter-spacing:.08em;font-weight:700">Clínicas Llenas</p>
      <h1 style="margin:0;font-size:22px;font-weight:800;color:#fff">🔔 Nuevo lead recibido</h1>
    </div>
    <div style="padding:28px 32px">
      <table style="width:100%;border-collapse:collapse">
        <tr>
          <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;font-size:13px;color:#94A3B8;font-weight:600;width:120px">Nombre</td>
          <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;font-size:15px;color:#0D1B2A;font-weight:700">${nombre}</td>
        </tr>
        <tr>
          <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;font-size:13px;color:#94A3B8;font-weight:600">Clínica</td>
          <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;font-size:15px;color:#0D1B2A">${clinica || '—'}</td>
        </tr>
        <tr>
          <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;font-size:13px;color:#94A3B8;font-weight:600">Email</td>
          <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;font-size:15px;color:#2563EB"><a href="mailto:${email}" style="color:#2563EB">${email}</a></td>
        </tr>
        <tr>
          <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;font-size:13px;color:#94A3B8;font-weight:600">Teléfono</td>
          <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;font-size:15px;color:#0D1B2A">${telefono || '—'}</td>
        </tr>
        <tr>
          <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;font-size:13px;color:#94A3B8;font-weight:600">Tipo clínica</td>
          <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;font-size:15px;color:#0D1B2A">${tipo || '—'}</td>
        </tr>
        ${mensaje ? `<tr>
          <td colspan="2" style="padding:16px 0 0">
            <p style="margin:0 0 8px;font-size:13px;color:#94A3B8;font-weight:600">Mensaje</p>
            <div style="background:#F8FAFC;border-radius:10px;padding:14px 16px;font-size:14px;color:#334155;line-height:1.6;border-left:3px solid #2563EB">${mensaje}</div>
          </td>
        </tr>` : ''}
      </table>
      <div style="margin-top:24px;text-align:center">
        <a href="mailto:${email}?subject=Re: Tu diagnóstico gratuito — Clínicas Llenas" style="display:inline-block;background:#2563EB;color:#fff;text-decoration:none;border-radius:50px;padding:13px 28px;font-weight:700;font-size:14px">Responder a ${nombre} →</a>
      </div>
    </div>
    <div style="padding:16px 32px;background:#F8FAFC;text-align:center;font-size:11px;color:#94A3B8">
      Lead recibido el ${new Date().toLocaleDateString('es-ES', { weekday:'long', year:'numeric', month:'long', day:'numeric', hour:'2-digit', minute:'2-digit' })} · clinicasllenas.com
    </div>
  </div>`;

  // HTML del email de confirmación que recibe el cliente
  const htmlCliente = `
  <div style="font-family:Inter,sans-serif;max-width:580px;margin:0 auto;background:#fff;border-radius:16px;overflow:hidden;border:1px solid #e2e8f0">
    <div style="background:linear-gradient(135deg,#0D1B2A,#1E3A5F);padding:32px 32px 28px;text-align:center">
      <p style="margin:0 0 8px;font-size:12px;color:#94A3B8;text-transform:uppercase;letter-spacing:.08em;font-weight:700">Clínicas Llenas</p>
      <h1 style="margin:0 0 8px;font-size:24px;font-weight:800;color:#fff">¡Recibido, ${nombre}! 🎉</h1>
      <p style="margin:0;font-size:15px;color:#94A3B8">Tu diagnóstico gratuito está en camino</p>
    </div>
    <div style="padding:32px 32px 24px">
      <p style="font-size:16px;color:#334155;line-height:1.7;margin:0 0 20px">Hola <strong>${nombre}</strong>,</p>
      <p style="font-size:16px;color:#334155;line-height:1.7;margin:0 0 20px">Hemos recibido tu solicitud de diagnóstico gratuito para <strong>${clinica || 'tu clínica'}</strong>. Nos pondremos en contacto contigo en las próximas <strong>24 horas laborables</strong>.</p>
      <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:12px;padding:18px 20px;margin:24px 0">
        <p style="margin:0 0 12px;font-size:13px;font-weight:700;color:#059669;text-transform:uppercase;letter-spacing:.05em">Lo que analizaremos en tu diagnóstico</p>
        <ul style="margin:0;padding-left:18px;font-size:14px;color:#334155;line-height:1.9">
          <li>Cuántos ingresos estás perdiendo por no-shows</li>
          <li>Qué pacientes dormidos puedes reactivar esta semana</li>
          <li>Cómo mejorar tus reseñas en Google rápidamente</li>
          <li>Plan de automatización personalizado para tu clínica</li>
        </ul>
      </div>
      <p style="font-size:15px;color:#64748B;line-height:1.7;margin:0 0 24px">Mientras tanto, si tienes alguna pregunta urgente, puedes escribirnos directamente respondiendo a este email.</p>
      <div style="text-align:center">
        <a href="https://clinicasllenas.com/blog/" style="display:inline-block;background:#0D1B2A;color:#fff;text-decoration:none;border-radius:50px;padding:13px 28px;font-weight:700;font-size:14px">Leer el blog mientras esperas →</a>
      </div>
    </div>
    <div style="padding:20px 32px;background:#F8FAFC;text-align:center;border-top:1px solid #e2e8f0">
      <p style="margin:0 0 6px;font-size:13px;color:#64748B">Clínicas Llenas · Automatización WhatsApp para clínicas privadas</p>
      <p style="margin:0;font-size:12px;color:#94A3B8"><a href="https://clinicasllenas.com" style="color:#2563EB;text-decoration:none">clinicasllenas.com</a></p>
    </div>
  </div>`;

  try {
    // Enviar email al equipo
    const r1 = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: 'Clínicas Llenas <hola@clinicasllenas.com>',
        to: ['woorkiaconsulting@gmail.com'],
        reply_to: email,
        subject: `🔔 Nuevo lead: ${nombre} — ${clinica || 'sin clínica'} (${tipo || '?'})`,
        html: htmlEquipo,
      }),
    });

    if (!r1.ok) {
      const err = await r1.json();
      throw new Error(err.message || 'Error al enviar email al equipo');
    }

    // Enviar confirmación al cliente
    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: 'Clínicas Llenas <hola@clinicasllenas.com>',
        to: [email],
        subject: `¡Recibido, ${nombre}! Tu diagnóstico está en camino 🎉`,
        html: htmlCliente,
      }),
    });

    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error('Resend error:', err.message);
    return res.status(500).json({ error: err.message });
  }
}
