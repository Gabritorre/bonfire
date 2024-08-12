from config import engine
from models import *
from sqlalchemy import text

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
print("Creating triggers...")


# example trigger
with engine.connect() as connection:
	connection.execute(text("""
		CREATE OR REPLACE FUNCTION check_budget() 
		RETURNS TRIGGER AS $$
		BEGIN
			IF NEW.budget < 0 THEN
				RAISE EXCEPTION 'Budget cannot be negative';
			END IF;
			RETURN NEW;
		END;
		$$ LANGUAGE plpgsql;

		CREATE OR REPLACE TRIGGER check_budget_trigger
		BEFORE INSERT OR UPDATE ON ad_campaigns
		FOR EACH ROW
		EXECUTE FUNCTION check_budget();
	"""))
	connection.commit()

print("Done.")