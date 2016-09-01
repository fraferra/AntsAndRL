import java.util.*;
import java.io.IOException;

public class HunterBot extends Bot {
	public static void main(String[] args) throws IOException {
		new HunterBot().readSystemInput();
	}

	public void doTurn() {
		Set<Tile> destinations = new HashSet<Tile>();
		Set<Tile> targets = new HashSet<Tile>();
		targets.addAll(getAnts().getFoodTiles());
		targets.addAll(getAnts().getEnemyAnts());
		for (Tile location : getAnts().getMyAnts()) {
			boolean issued = false;
			Tile closestTarget = null;
			int closestDistance = 999999;
			for (Tile target : targets) {
				int distance = getAnts().getDistance(location, target);
				if (distance < closestDistance) {
					closestDistance = distance;
					closestTarget = target;
				}
			}
			if (closestTarget != null) {
				List<Aim> directions = getAnts().getDirections(location, closestTarget);
				Collections.shuffle(directions);
				for (Aim direction : directions) {
					Tile destination = getAnts().getTile(location, direction);
					if (getAnts().getIlk(destination).isUnoccupied() && !destinations.contains(destination)) {
						getAnts().issueOrder(location, direction);
						destinations.add(destination);
						issued = true;
						break;
					}
				}
			}
			if (!issued) {
				destinations.add(location);
			}
		}
	}
}
