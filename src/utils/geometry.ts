/**
 * Utility functions for spatial geometry, coordinate verification, and 3-node triangular arrangement check.
 */

export interface LatLng {
  lat: number;
  lng: number;
}

export interface NodeWithCoords {
  coordinates?: LatLng;
  latitude?: number;
  longitude?: number;
}

export interface TriangleCheckResult {
  isTriangular: boolean;
  isCollinear: boolean;
  warningMessage: string | null;
}

/**
 * Checks if 3 nodes form a valid non-collinear spatial triangle.
 * Requirement 6: If configured nodes are not spatially arranged correctly (collinear or degenerate),
 * display a configuration warning without silently modifying node positions.
 */
export function checkTriangularArrangement(nodes: NodeWithCoords[]): TriangleCheckResult {
  if (!nodes || nodes.length !== 3) {
    return {
      isTriangular: true,
      isCollinear: false,
      warningMessage: null,
    };
  }

  const coords: LatLng[] = nodes.map((n) => {
    if (n.coordinates) return n.coordinates;
    return {
      lat: n.latitude || 0,
      lng: n.longitude || 0,
    };
  });

  const [p1, p2, p3] = coords;

  // Calculate triangle area in coordinate space: 0.5 * |x1(y2 - y3) + x2(y3 - y1) + x3(y1 - y2)|
  const area = Math.abs(
    p1.lat * (p2.lng - p3.lng) +
    p2.lat * (p3.lng - p1.lng) +
    p3.lat * (p1.lng - p2.lng)
  ) * 0.5;

  const d12 = Math.hypot(p2.lat - p1.lat, p2.lng - p1.lng);
  const d23 = Math.hypot(p3.lat - p2.lat, p3.lng - p2.lng);
  const d31 = Math.hypot(p1.lat - p3.lat, p1.lng - p3.lng);

  const maxDist = Math.max(d12, d23, d31);

  if (maxDist < 1e-6) {
    return {
      isTriangular: false,
      isCollinear: true,
      warningMessage: 'Configuration Warning: Deployed nodes have identical or overlapping GPS coordinates.',
    };
  }

  // Height of triangle relative to longest side
  const h = (2 * area) / maxDist;
  const aspectRatio = h / maxDist;

  // If height is less than 8% of longest side, the 3 nodes are practically in a straight line
  if (aspectRatio < 0.08) {
    return {
      isTriangular: false,
      isCollinear: true,
      warningMessage:
        'Configuration Warning: The 3 configured Bio-Sniff nodes are collinear (in a straight line). Multi-node spatial triangulation operates optimally with a triangular arrangement around the field perimeter.',
    };
  }

  return {
    isTriangular: true,
    isCollinear: false,
    warningMessage: null,
  };
}
