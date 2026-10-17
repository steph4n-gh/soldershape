"use strict";

window.SolderMesh = Object.freeze({
  drawSurface(ctx, mesh, project, standoffMm, wireframe) {
    const projected = mesh.vertices_mm.map(project);
    const faces = mesh.triangles.map((triangle) => {
      const points = triangle.map((index) => projected[index]);
      const vertices = triangle.map((index) => mesh.vertices_mm[index]);
      const a = vertices[0], b = vertices[1], c = vertices[2];
      const ux = b[0] - a[0], uy = b[1] - a[1], uz = b[2] - a[2];
      const vx = c[0] - a[0], vy = c[1] - a[1], vz = c[2] - a[2];
      const normal = [uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx];
      const magnitude = Math.hypot(...normal) || 1;
      const light = Math.max(0, (normal[0] * -0.35 + normal[1] * -0.4 + normal[2] * 0.85) / magnitude);
      const shade = 0.62 + 0.38 * light;
      const flatCap = Math.abs(a[2] - b[2]) < 1e-9 && Math.abs(a[2] - c[2]) < 1e-9 && (Math.abs(a[2]) < 1e-8 || Math.abs(a[2] - standoffMm) < 1e-8);
      const base = flatCap ? [198, 139, 91] : [173, 199, 214];
      return { points, depth: (points[0][2] + points[1][2] + points[2][2]) / 3, color: `rgb(${base.map((component) => Math.round(component * shade)).join(",")})` };
    });
    faces.sort((a, b) => a.depth - b.depth);
    for (const face of faces) {
      ctx.beginPath();
      ctx.moveTo(face.points[0][0], face.points[0][1]);
      ctx.lineTo(face.points[1][0], face.points[1][1]);
      ctx.lineTo(face.points[2][0], face.points[2][1]);
      ctx.closePath();
      ctx.fillStyle = face.color;
      ctx.fill();
      ctx.strokeStyle = wireframe ? "#213e5270" : face.color;
      ctx.lineWidth = wireframe ? 0.5 : 0.45;
      ctx.stroke();
    }
  },
});
