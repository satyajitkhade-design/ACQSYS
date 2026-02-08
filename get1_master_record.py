"""
GET1 - GET NEXT RECORD: MM77(pm) ME MASTER
This module implements the master record retrieval logic from the pseudocode specification.
"""

import logging
from typing import List, Dict, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MasterRecordException(Exception):
    """Custom exception for master record processing errors."""
    pass


class SequenceError(MasterRecordException):
    """Raised when records are out of sequence."""
    pass


class EndOfFileError(MasterRecordException):
    """Raised when end of file is reached."""
    pass


class MasterRecordProcessor:
    """
    Processes merchant master records from MM77 table.
    
    Attributes:
        mm77_records: List of master records (each record is a dict with fields like M100, M101)
        pm: Pointer to current position in MM77
        psort1: Previous sort key value for sequence validation
        isort1: Current sort key value
    """
    
    def __init__(self, mm77_records: List[Dict]):
        """
        Initialize the processor with master records.
        
        Args:
            mm77_records: List of master record dictionaries containing at least:
                         - M100: Record type (P=PARENT, other=DETAIL)
                         - M101: MEID (Merchant ID) - first digit determines record type
                         - Other fields as needed for ISORT1 formation
        """
        self.mm77_records = mm77_records
        self.pm = -1  # Pointer to current row (starts at -1, will be incremented to 0)
        self.psort1 = None  # Previous ISORT1 value
        self.isort1 = None  # Current ISORT1 value
        self.eof_reached = False
    
    def get_next_record(self) -> Optional[Dict]:
        """
        GET1 - Retrieve the next valid merchant master record.
        
        Logic Flow:
        1. Increment pointer to next row of MM77
        2. Check if first digit of M101 (MEID) is "Z" (end-of-file marker)
        3. Skip parent records (M100 = "P")
        4. Form ISORT1 from record fields
        5. Validate sequence (ISORT1 > PSORT1)
        6. Update PSORT1 and return the record
        
        Returns:
            The next valid master record dictionary, or None if EOF
            
        Raises:
            SequenceError: If ISORT1 is not greater than PSORT1
            EndOfFileError: When end-of-file is reached
        """
        try:
            while True:
                # G1: Increment pointer to next row of MM77
                self.pm += 1
                logger.info(f"GET1: Incrementing pointer to pm={{self.pm}}")
                
                # Check bounds
                if self.pm >= len(self.mm77_records):
                    # End of file condition
                    self.isort1 = "Z" * 10  # All "Z"s represents EOF
                    self.eof_reached = True
                    logger.info("GET1: End of file reached - all records processed")
                    self._validate_sequence()
                    return None
                
                current_record = self.mm77_records[self.pm]
                logger.info(f"GET1: Processing record at pm={{self.pm}}: {{current_record}}")
                
                # G10: Check if first digit of M101 (MEID) is "Z"
                meid = current_record.get('M101', '')
                if not meid:
                    logger.warning(f"GET1: Record at pm={{self.pm}} missing M101 (MEID) field")
                    continue
                
                first_digit_meid = str(meid)[0]
                
                if first_digit_meid != "Z":
                    logger.debug(f"GET1: MEID first digit '{{first_digit_meid}}' is not 'Z', processing record")
                    
                    # G10: Check if M100 = "P" (PARENT) - bypass parent records
                    m100 = current_record.get('M100', '')
                    if m100 == "P":
                        logger.info(f"GET1: Record at pm={{self.pm}} is PARENT (M100='P'), bypassing")
                        continue  # Go back to GET1 - fetch next record
                    
                    # Form ISORT1 from the record
                    self.isort1 = self._form_isort1(current_record)
                    logger.info(f"GET1: Formed ISORT1='{{self.isort1}}'")
                else:
                    # First digit is "Z" - EOF condition
                    logger.info(f"GET1: MEID starts with 'Z' - EOF marker detected")
                    self.isort1 = "Z" * 10  # All "Z"s
                    self.eof_reached = True
                
                # G11: Validate sequence - ISORT1 must be > PSORT1
                self._validate_sequence()
                
                # G13: Update PSORT1 with current ISORT1
                self.psort1 = self.isort1
                logger.info(f"GET1: Updated PSORT1='{{self.psort1}}'")
                
                # Return the processed record
                if self.eof_reached:
                    return None
                
                return current_record
        
        except SequenceError as e:
            logger.error(f"GET1: Sequence error - {{str(e)}}")
            raise
    
    def _validate_sequence(self) -> None:
        """
        G11: Validate that ISORT1 > PSORT1.
        
        Raises:
            SequenceError: If sequence is invalid (ISORT1 <= PSORT1)
        """
        if self.psort1 is None:
            # First record - no previous value to compare
            logger.info(f"GET1: First record - no sequence validation needed")
            return
        
        if self.isort1 <= self.psort1:
            error_msg = (
                f"Sequence Error: ISORT1 ('{{self.isort1}}') must be > PSORT1 ('{{self.psort1}}'). "
                f"Records are out of sequence."
            )
            logger.error(error_msg)
            raise SequenceError(error_msg)
        
        logger.debug(f"GET1: Sequence valid - ISORT1 ('{{self.isort1}}') > PSORT1 ('{{self.psort1}}')")
    
    def _form_isort1(self, record: Dict) -> str:
        """
        Form ISORT1 from the master record fields.
        
        ISORT1 is typically a concatenation of key fields that define the sort order.
        This is a template - adjust field names based on actual data structure.
        
        Args:
            record: Master record dictionary
            
        Returns:
            ISORT1 string value
        """
        # Template implementation - customize based on your actual data structure
        # Common fields might be: Merchant ID, Chain ID, Store ID, etc.
        
        # Example: Concatenate M101 (MEID) with other key fields
        meid = record.get('M101', '').ljust(10, ' ')  # Pad to 10 chars
        
        # Add other sort key components as needed
        # Example: chain_id = record.get('CHAIN_ID', '').ljust(5, ' ')
        # isort1 = meid + chain_id
        
        isort1 = meid
        
        logger.debug(f"GET1: Formed ISORT1 from record fields: '{{isort1}}'")
        return isort1
    
    def process_all_records(self) -> List[Dict]:
        """
        Process all valid records until EOF.
        
        Returns:
            List of all valid (non-parent, non-EOF) master records
            
        Raises:
            SequenceError: If any record is out of sequence
        """
        valid_records = []
        
        try:
            while True:
                try:
                    record = self.get_next_record()
                    if record is None:
                        # EOF reached
                        logger.info("GET1: Processing complete - EOF reached")
                        break
                    valid_records.append(record)
                except EndOfFileError:
                    logger.info("GET1: EOF marker detected")
                    break
        
        except SequenceError as e:
            logger.error(f"GET1: Halting due to sequence error - {{str(e)}}")
            logger.info("GET1: Please restart after fixing the sequence error")
            raise
        
        return valid_records
    
    def reset(self) -> None:
        """Reset the processor state for reprocessing."""
        self.pm = -1
        self.psort1 = None
        self.isort1 = None
        self.eof_reached = False
        logger.info("GET1: Processor reset")


# Example usage and test cases
if __name__ == "__main__":
    # Example master records
    test_records = [
        {'M100': 'D', 'M101': 'A001', 'NAME': 'Merchant A'},
        {'M100': 'D', 'M101': 'B002', 'NAME': 'Merchant B'},
        {'M100': 'P', 'M101': 'C003', 'NAME': 'Parent Merchant C'},  # Will be skipped
        {'M100': 'D', 'M101': 'D004', 'NAME': 'Merchant D'},
        {'M100': 'D', 'M101': 'Z999', 'NAME': 'EOF Marker'},  # EOF
    ]
    
    print("=" * 60)
    print("GET1 Master Record Processor - Test Run")
    print("=" * 60)
    
    processor = MasterRecordProcessor(test_records)
    
    try:
        valid_records = processor.process_all_records()
        
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Total records processed: {{len(valid_records)}}")
        print(f"Final PSORT1: {{processor.psort1}}")
        print(f"EOF reached: {{processor.eof_reached}}")
        
        print("\nValid records:")
        for i, record in enumerate(valid_records, 1):
            print(f"  {{i}}. {{record}}")
    
    except SequenceError as e:
        print(f"\nERROR: {{str(e)}}")
        print("ACTION: Please restart after fixing the sequence error")
