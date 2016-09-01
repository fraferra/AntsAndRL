import java.util.*;
import java.io.IOException;

public class RandomBot extends Bot {
	public static void main(String[] args) throws IOException {
		new RandomBot().readSystemInput();
	}

	public void doTurn() {
		Set<Tile> destinations = new HashSet<Tile>();
		for (Tile location : getAnts().getMyAnts()) {
			List<Aim> directions = new ArrayList<Aim>(EnumSet.allOf(Aim.class));
			Collections.shuffle(directions);
			boolean issued = false;
			for (Aim direction : directions) {
				Tile destination = getAnts().getTile(location, direction);
				if (getAnts().getIlk(destination).isUnoccupied() && !destinations.contains(destination)) {
					getAnts().issueOrder(location, direction);
					destinations.add(destination);
					issued = true;
					break;
				}
			}
			if (!issued) {
				destinations.add(location);
			}
		}
	}
}
